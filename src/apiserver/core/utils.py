import os
from datetime import datetime, timedelta

from azure.storage.blob import generate_blob_sas, BlobSasPermissions

from dotenv import load_dotenv


def generate_image_sas_url(image, expiry_hours=24):
    """
    Generate SAS URLs for all PowerPoint files in the specified container.

    :param image: image file name.
    :param expiry_hours: The number of hours for which the SAS URL will be valid.
    :return: SAS URL.
    """

    account_name = os.environ['STORAGE_ACCOUNT_NAME']
    account_key = os.environ['STORAGE_ACCOUNT_KEY']
    container_name = os.environ['IMAGE_CONTAINER']

    sas_blob = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=image,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=expiry_hours),
    )
    image_sas_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{image}?{sas_blob}"

    return image_sas_url


if __name__ == '__main__':
    load_dotenv(verbose=False, dotenv_path='../../../.env.local')

    print(generate_image_sas_url('favicon11.png', expiry_hours=1))
