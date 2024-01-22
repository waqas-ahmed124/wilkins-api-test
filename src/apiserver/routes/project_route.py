from enum import Enum
from typing import List, Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, desc, update, func
from fastapi_sqlalchemy import db
from fastapi import APIRouter, Query, Depends, HTTPException

from apiserver.core.security import get_password_hash
from apiserver.core.utils import generate_image_sas_url
from apiserver.routes.auth_route import get_azure_user
from apiserver.service.api_crud import project_crud, submission_crud, vendor_crud, project_vendor_crud, user_crud, \
    user_project_crud
from apiserver.models import Project, ProjectStatusEnum, Submission, Vendor, ProjectVendor, User, UserProject
from apiserver.schemas import ProjectCreateIn, FetchAllProjectsSchema, \
    ProjectSubmissionsSchema, ProjectOut, SubmissionCreateIn, \
    SubmissionCreateOut, VendorCreateRequestSchema, UserCreateRequestSchema, UserCreateResponseSchema, \
    VendorCreateResponseSchema, SubmissionUpdateIn, SubmissionUpdateOut, ProjectStats, ProjectUpdateIn, \
    SelectedSubmissionIn, SelectedSubmissionOut


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class ProjectRouter:
    @property
    def router(self):
        api_router = APIRouter(prefix="/projects", tags=["Projects"])

        @api_router.get("", status_code=200, response_model=FetchAllProjectsSchema)
        def fetch_projects(
                status: List[ProjectStatusEnum] = Query(None),
                vendor: str = Query(None),
                client: str = Query(None),
                search: str = Query(None),
                limit: int = 10,
                skip: int = 0,
                user: dict = Depends(get_azure_user)
        ) -> Any:

            query = db.session.query(Project)
            if vendor or search:
                query = query.outerjoin(Project.project_vendors)
                query = query.outerjoin(ProjectVendor.vendor)
            if status:
                query = query.filter(Project.status.in_(status))
            if client:
                query = query.filter(Project.client == client)
            if vendor:
                query = query.filter(Vendor.name == vendor)
            if search:
                query = query.filter(or_(Project.wilkins_id.ilike(f'%%{search}%%'),
                                         Project.name.ilike(f'%%{search}%%'),
                                         Project.client.ilike(f'%%{search}%%'),
                                         Vendor.name.ilike(f'%%{search}%%')))

            total_records = query.count()
            query = query.order_by(desc(Project.created_at))
            query = query.limit(limit).offset(skip)
            records = query.all()

            data = []
            rec: Project
            for rec in records:
                data.append({
                    'wilkins_id': rec.wilkins_id,
                    'name': rec.name,
                    'client': rec.client,
                    'status': rec.status.value,
                    'budget': rec.budget,
                    'vendors': [project_vendor.vendor.name for project_vendor in rec.project_vendors]
                })

            resp = {
                'data': data,
                'total_records': total_records
            }

            return resp

        @api_router.post("", status_code=201, response_model=ProjectOut)
        def create_project(project_in: ProjectCreateIn, user: dict = Depends(get_azure_user)) -> Any:
            return project_crud.create(obj_in=project_in)

        @api_router.put("/{wilkins_id}", status_code=200, response_model=ProjectOut)
        def update_project(
                wilkins_id: str,
                project_update: ProjectUpdateIn,
                user: dict = Depends(get_azure_user)
        ) -> Any:

            project = db.session.query(Project).filter(Project.wilkins_id == wilkins_id).first()
            if project is None:
                raise HTTPException(404, 'Project not found!')

            return project_crud.update(db_obj=project, obj_in=project_update)

        @api_router.get("/{wilkins_id}/submissions", status_code=200, response_model=ProjectSubmissionsSchema)
        def fetch_project_submissions(
                wilkins_id: str,
                state: str = Query(None),
                town: str = Query(None),
                media_type: str = Query(None),
                vendor: str = Query(None),
                illuminated: bool = Query(None),
                selected: bool = Query(None),
                sort_column: str = Query(None),
                sort_order: SortOrder = Query(None),
                search: str = Query(None),
                limit: int = 10,
                skip: int = 0,
                user: dict = Depends(get_azure_user)
        ) -> Any:

            project = db.session.query(Project).filter(Project.wilkins_id == wilkins_id).first()
            if project is None:
                raise HTTPException(status_code=400, detail='Project not found!')

            query = db.session.query(Submission)
            query = query.join(Submission.project)
            query = query.filter(Project.wilkins_id == wilkins_id)

            if vendor or search:
                query = query.join(Submission.vendor)

            if state:
                query = query.filter(Submission.state == state)
            if town:
                query = query.filter(Submission.town == town)
            if media_type:
                query = query.filter(Submission.media_type == media_type)
            if vendor:
                query = query.filter(Vendor.name == vendor)
            if illuminated is not None:
                query = query.filter(Submission.is_illuminated.is_(illuminated))
            if selected is not None:
                query = query.filter(Submission.selected.is_(selected))

            if search:
                query = query.filter(or_(
                    Vendor.name.ilike(f'%%{search}%%'),
                    Submission.unit_id.ilike(f'%%{search}%%'),
                    Submission.town.ilike(f'%%{search}%%'),
                    Submission.market.ilike(f'%%{search}%%'),
                    Submission.state.ilike(f'%%{search}%%'),
                    Submission.media_type.ilike(f'%%{search}%%'),
                    Submission.facing.ilike(f'{search}%%'),
                ))

            total_records = query.count()

            if sort_column:
                sort_criteria = getattr(getattr(Submission, sort_column), sort_order)()
                query = query.order_by(sort_criteria)

            query = query.limit(limit).offset(skip)
            records = query.all()

            data = []
            rec: Submission
            for rec in records:
                data.append({
                    'vendor': rec.vendor.name,
                    'unit_id': rec.unit_id,
                    'unit': rec.unit,
                    'town': rec.town,
                    'state': rec.state,
                    'market': rec.market,
                    'location_description': rec.location_description,
                    'geopath_id': rec.geopath_id,
                    'target_location': rec.target_location,
                    'a18_weekly_impressions': rec.a18_weekly_impressions,
                    'a18_4wk_reach': rec.a18_4wk_reach,
                    'a18_4wk_freq': rec.a18_4wk_freq,
                    'availability_start': rec.availability_start,
                    'availability_end': rec.availability_end,
                    'total_units': rec.total_units,
                    'installation_cost': rec.installation_cost,
                    'markup_percentage': rec.markup_percentage,
                    'is_prod_forced': rec.is_prod_forced,
                    'taxes': rec.taxes,
                    'four_week_rate_card': rec.four_week_rate_card,
                    'internal_four_week_media_cost': rec.internal_four_week_media_cost,
                    'additional_installation_cost': rec.additional_installation_cost,
                    'unit_highlights': rec.unit_highlights,
                    'no_of_spots_per_loop': rec.no_of_spots_per_loop,
                    'spot_length_secs': rec.spot_length_secs,
                    'distance_to_location': rec.distance_to_location,
                    'media_type': rec.media_type,
                    'facing': rec.facing,
                    'is_illuminated': rec.is_illuminated,
                    'one_week_media_cost': rec.one_week_media_cost,
                    'two_week_media_cost': rec.two_week_media_cost,
                    'three_week_media_cost': rec.three_week_media_cost,
                    'four_week_media_cost': rec.four_week_media_cost,
                    'initial_installation_cost': rec.initial_installation_cost,
                    'production_cost': rec.production_cost,
                    'latitude': rec.latitude,
                    'longitude': rec.longitude,
                    'selected': rec.selected,
                    'size': rec.size,
                    'no_of_periods': rec.no_of_periods,
                    'image_id': rec.image_id,
                    'image_url': generate_image_sas_url(rec.image_id) if rec.image_id is not None else None,
                })

            resp = {
                'data': data,
                'total_records': total_records
            }

            return resp

        @api_router.post("/{wilkins_id}/submissions", status_code=201, response_model=SubmissionCreateOut)
        def create_submission(
                wilkins_id: str,
                submission_in: SubmissionCreateIn,
                user: dict = Depends(get_azure_user)
        ) -> Any:

            submission = db.session.query(Submission).filter(Submission.unit_id == submission_in.unit_id).first()

            if submission is None:
                vendor = db.session.query(Vendor).filter(Vendor.name == submission_in.vendor).first()

                if vendor is None:
                    vendor_data = {
                        'name': submission_in.vendor,
                        'emails': [submission_in.vendor_email] if submission_in.vendor_email is not None else []
                    }
                    vendor = vendor_crud.create(vendor_data)

                project = db.session.query(Project).filter(Project.wilkins_id == wilkins_id).first()
                if project is None:
                    raise HTTPException(status_code=404, detail="Project not found!")

                query = db.session.query(ProjectVendor)
                query = query.filter(ProjectVendor.project_id == project.id,
                                     ProjectVendor.vendor_id == vendor.id)
                project_vendor = query.first()

                if project_vendor is None:
                    project_vendor_in = {
                        'vendor_id': vendor.id,
                        'project_id': project.id,
                    }
                    project_vendor_crud.create(project_vendor_in)

                submission_in_dict = jsonable_encoder(submission_in)
                submission_in_dict.pop('vendor_email')
                submission_in_dict.pop('vendor')
                submission_in_dict['project_id'] = project.id
                submission_in_dict['vendor_id'] = vendor.id
                return submission_crud.create(obj_in=submission_in_dict)

            else:
                if submission.user_locked and user['is_cli_user']:
                    raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")

                return submission_crud.update(db_obj=submission, obj_in=submission_in)

        @api_router.patch("/{wilkins_id}/submissions/{unit_id}", status_code=200, response_model=SubmissionUpdateOut)
        def update_submission(
                wilkins_id: str,
                unit_id: str,
                submission_update: SubmissionUpdateIn,
                user: dict = Depends(get_azure_user)
        ) -> Any:

            submission = db.session.query(Submission).filter(Submission.unit_id == unit_id).first()

            if submission is None:
                raise HTTPException(status_code=404, detail="Submission not found!")

            submission_update = submission_update.model_dump(exclude_unset=True)

            if not submission.user_locked:
                submission_update['user_locked'] = True

            return submission_crud.update(db_obj=submission, obj_in=submission_update)

        @api_router.get("/clients", status_code=200, response_model=List[str])
        def fetch_project_clients(search: str = Query(None), user: dict = Depends(get_azure_user)) -> Any:

            query = db.session.query(Project.client)
            query = query.filter(Project.client.isnot(None))
            if search:
                query = query.filter(Project.client.ilike(f'%%{search}%%'))

            query = query.distinct()
            query = query.limit(10)
            records = query.all()

            resp = [rec.client for rec in records]

            return resp

        @api_router.get("/vendors", status_code=200, response_model=List[str])
        def fetch_project_vendors(
                search: str = Query(None),
                user: dict = Depends(get_azure_user)
        ) -> Any:

            query = db.session.query(Vendor.name)

            if search:
                query = query.filter(Vendor.name.ilike(f'%%{search}%%'))

            query = query.limit(10)
            records = query.all()

            resp = [rec.name for rec in records]

            return resp

        @api_router.put("/{wilkins_id}/select-submissions", status_code=200, response_model=SelectedSubmissionOut)
        def select_submissions(
                wilkins_id: str,
                selected_submissions: SelectedSubmissionIn,
                user: dict = Depends(get_azure_user)
        ) -> Any:
            project = db.session.query(Project).filter(Project.wilkins_id == wilkins_id).first()
            if project is None:
                raise HTTPException(status_code=400, detail='Project not found!')

            stmt = update(Submission).where(Submission.unit_id.in_(selected_submissions.unit_ids)).values(selected=selected_submissions.selected)
            db.session.execute(stmt)
            db.session.commit()

            query = db.session.query(func.sum(Submission.a18_weekly_impressions).label('impressions'),
                                     func.count(Submission.id).label('selected'))
            query = query.filter(Submission.project_id == project.id)
            query = query.filter(Submission.selected.is_(True))
            result = query.one_or_none()

            query = db.session.query(Submission)
            query = query.filter(Submission.project_id == project.id)
            query = query.filter(Submission.selected.is_(True))
            submissions = query.all()

            total_media_cost = sum(rec.total_media_cost for rec in submissions if rec.total_media_cost is not None)
            # total_cost = sum(rec.total_cost for rec in submissions if rec.total_cost is not None)

            if result.impressions is not None and result.impressions > 0:
                cpm = total_media_cost / result.impressions * 1000
            else:
                cpm = 0

            resp = {
                'selected': result.selected,
                'impressions': result.impressions,
                'cpm': cpm,
                'estimated_budget': total_media_cost
            }

            return resp

        @api_router.get("/{wilkins_id}/submission-media-types", status_code=200, response_model=List[str])
        def fetch_project_submission_media_types(
                wilkins_id: str,
                search: str = Query(None),
                state: str = Query(None),
                town: str = Query(None),
                user: dict = Depends(get_azure_user)
        ) -> Any:

            query = db.session.query(Submission.media_type)
            query = query.filter(Submission.media_type.isnot(None))

            query = query.join(Submission.project)
            query = query.filter(Project.wilkins_id == wilkins_id)

            if state:
                query = query.filter(Submission.state == state)

            if town:
                query = query.filter(Submission.town == town)

            if search:
                query = query.filter(Submission.media_type.ilike(f'%%{search}%%'))

            query = query.distinct()
            query = query.limit(10)
            records = query.all()

            resp = [rec.media_type for rec in records]

            return resp

        @api_router.get("/{wilkins_id}/submission-locations", status_code=200, response_model=List[str])
        def fetch_project_submission_locations(
                wilkins_id: str,
                search: str = Query(None),
                state: str = Query(None),
                user: dict = Depends(get_azure_user)
        ) -> Any:

            query = db.session.query(Submission.town)
            query = query.filter(Submission.town.isnot(None))

            query = query.join(Submission.project)
            query = query.filter(Project.wilkins_id == wilkins_id)

            if state:
                query = query.filter(Submission.state == state)

            if search:
                query = query.filter(Submission.town.ilike(f'%%{search}%%'))

            query = query.distinct()
            query = query.limit(10)
            records = query.all()

            resp = [rec.town for rec in records]

            return resp

        @api_router.get("/{wilkins_id}/submission-states", status_code=200, response_model=List[str])
        def fetch_project_submission_states(
                wilkins_id: str,
                search: str = Query(None),
                user: dict = Depends(get_azure_user)
        ) -> Any:

            query = db.session.query(Submission.state)
            query = query.filter(Submission.state.isnot(None))

            query = query.join(Submission.project)
            query = query.filter(Project.wilkins_id == wilkins_id)
            if search:
                query = query.filter(Submission.state.ilike(f'%%{search}%%'))

            query = query.distinct()
            query = query.limit(10)
            records = query.all()

            resp = [rec.state for rec in records]

            return resp

        @api_router.get("/{wilkins_id}/submission-vendors", status_code=200, response_model=List[str])
        def fetch_project_submission_vendors(
                wilkins_id: str,
                search: str = Query(None),
                state: str = Query(None),
                town: str = Query(None),
                media_type: str = Query(None),
                user: dict = Depends(get_azure_user)
        ) -> Any:

            query = db.session.query(Vendor.name)
            query = query.join(ProjectVendor.vendor)
            query = query.join(ProjectVendor.project)
            query = query.filter(Project.wilkins_id == wilkins_id)

            if state or town or media_type:
                query = query.join(Submission, Submission.id == Project.id)

            if state:
                query = query.filter(Submission.state == state)

            if town:
                query = query.filter(Submission.town == town)

            if media_type:
                query = query.filter(Submission.media_type == media_type)

            if search:
                query = query.filter(Vendor.name.ilike(f'%%{search}%%'))

            query = query.limit(10)
            records = query.all()

            resp = [rec.name for rec in records]

            return resp

        @api_router.get("/{wilkins_id}/stats", status_code=200, response_model=ProjectStats)
        def fetch_project_stats(
                wilkins_id: str,
                user: dict = Depends(get_azure_user)
        ) -> Any:

            project = db.session.query(Project).filter(Project.wilkins_id == wilkins_id).first()

            if project is None:
                raise HTTPException(status_code=404, detail="Project not found!")

            total_submissions = db.session.query(func.count(Submission.id)).filter(Submission.project_id == project.id).scalar()

            vendors_in_project = db.session.query(ProjectVendor.id).filter(ProjectVendor.project_id == project.id).count()

            query = db.session.query(Submission.vendor_id).filter(Submission.project_id == project.id)
            vendors_in_submission = query.distinct().count()

            query = db.session.query(func.sum(Submission.a18_weekly_impressions).label('impressions'),
                                     func.count(Submission.id).label('selected'))
            query = query.filter(Submission.project_id == project.id)
            query = query.filter(Submission.selected.is_(True))
            result = query.one_or_none()

            query = db.session.query(Submission)
            query = query.filter(Submission.project_id == project.id)
            query = query.filter(Submission.selected.is_(True))
            submissions = query.all()

            total_media_cost = sum(rec.total_media_cost for rec in submissions if rec.total_media_cost is not None)
            # total_cost = sum(rec.total_cost for rec in submissions if rec.total_cost is not None)

            if result.impressions is not None and result.impressions > 0:
                cpm = total_media_cost / result.impressions * 1000
            else:
                cpm = 0

            resp = {
                "project_name": project.name,
                "vendors_in_project": vendors_in_project,
                "vendors_in_submission": vendors_in_submission,
                "sites": total_submissions,
                "total_budget": project.budget,
                "selected": result.selected,
                "impressions": result.impressions,
                "cpm": cpm,
                "estimated_budget": total_media_cost
            }

            return resp

        @api_router.get("/{wilkins_id}", status_code=200, response_model=ProjectOut)
        def fetch_project(
                wilkins_id: str,
                user: dict = Depends(get_azure_user)
        ) -> Any:

            project = db.session.query(Project).filter(Project.wilkins_id == wilkins_id).first()

            if project is None:
                raise HTTPException(status_code=404, detail="Project not found!")

            return project

        @api_router.post("/{wilkins_id}/vendors", status_code=201, response_model=VendorCreateResponseSchema)
        def create_vendor(
                vendor_in: VendorCreateRequestSchema,
                wilkins_id: str,
                user: dict = Depends(get_azure_user)
        ) -> Any:

            vendor = db.session.query(Vendor).filter(Vendor.name == vendor_in.name).first()

            if vendor is None:
                vendor = vendor_crud.create(vendor_in)

            project = db.session.query(Project).filter(Project.wilkins_id == wilkins_id).first()

            if project is None:
                raise HTTPException(status_code=404, detail="Project not found!")

            query = db.session.query(ProjectVendor)
            query = query.filter(ProjectVendor.project_id == project.id)
            query = query.filter(ProjectVendor.vendor_id == vendor.id)
            project_vendor = query.first()

            if project_vendor is None:
                project_vendor_in = {
                    'vendor_id': vendor.id,
                    'project_id': project.id,
                }
                project_vendor_crud.create(project_vendor_in)

            return vendor

        @api_router.post("/{wilkins_id}/users", status_code=201, response_model=UserCreateResponseSchema)
        def create_user(
                user_in: UserCreateRequestSchema,
                wilkins_id: str,
                user: dict = Depends(get_azure_user)
        ) -> Any:

            if not user['is_cli_user']:
                raise HTTPException(status_code=403, detail="You do not have permission to create this resource.")

            user = db.session.query(User).filter(User.email == user_in.email).first()

            if user is None:
                user_in.password = get_password_hash(user_in.password)
                user = user_crud.create(user_in)

            project = db.session.query(Project).filter(Project.wilkins_id == wilkins_id).first()

            if project is None:
                raise HTTPException(status_code=404, detail="Project not found!")

            query = db.session.query(UserProject)
            query = query.filter(UserProject.user_id == user.id)
            query = query.filter(UserProject.project_id == project.id)
            user_project = query.first()

            if user_project is None:
                user_project_in = {
                    'user_id': user.id,
                    'project_id': project.id,
                }
                user_project_crud.create(user_project_in)

            return user

        return api_router
