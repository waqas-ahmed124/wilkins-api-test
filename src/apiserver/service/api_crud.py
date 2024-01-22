from apiserver.service.base_crud import CRUDBase
from apiserver.models import Project, Submission, Vendor, ProjectVendor, User, UserProject


class ProjectCrud(CRUDBase):
    pass


project_crud = ProjectCrud(Project)


class SubmissionCrud(CRUDBase):
    pass


submission_crud = SubmissionCrud(Submission)


class VendorCrud(CRUDBase):
    pass


vendor_crud = VendorCrud(Vendor)


class ProjectVendorCrud(CRUDBase):
    pass


project_vendor_crud = ProjectVendorCrud(ProjectVendor)


class UserCrud(CRUDBase):
    pass


user_crud = UserCrud(User)


class UserProjectCrud(CRUDBase):
    pass


user_project_crud = UserProjectCrud(UserProject)
