from modelscope.hub.snapshot_download import snapshot_download
from pydantic import BaseModel, Field


class Download_Util(BaseModel):
    download_dir: str = Field(...,
                              description="The directory to save the downloaded model")
    model_name: str = Field(..., description="The model name to download")
    revision: str = Field(
        'master', description="The revision of the model to download")

    def download_model(self):
        try:
            snapshot_download(
                self.model_name, cache_dir=self.download_dir, revision=self.revision)
        except Exception as e:
            print(e)
