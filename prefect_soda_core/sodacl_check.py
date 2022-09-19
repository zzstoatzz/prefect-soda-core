"""SodaCL check block"""
from typing import Optional

from prefect.blocks.core import Block
from pydantic import HttpUrl, root_validator
from yaml import safe_dump, safe_load
from yaml.error import YAMLError

from prefect_soda_core.exceptions import SodaConfigurationException


class SodaCLCheck(Block):
    """
    This block represents a SodaCL check that can be used when running Soda scans.
    """

    sodacl_yaml_path: str
    sodacl_yaml_str: Optional[str]

    _block_type_name: Optional[str] = "SodaCL Check"
    _logo_url: Optional[HttpUrl] = "https://www.to.do"  # noqa

    @root_validator(pre=True)
    def check_block_configuration(cls, values):
        """
        Ensure that the configuration options are valid
        """
        sodacl_yaml_str_exists = bool(values.get("sodacl_yaml_str"))

        # If the YAML string is passed, but is not a valid YAML, then raise error
        if sodacl_yaml_str_exists:
            try:
                yaml_str = values.get("sodacl_yaml_str")
                safe_load(yaml_str)
            except YAMLError as exc:
                msg = f"The provided checks YAML is not valid. Error is: {exc}"
                raise SodaConfigurationException(msg)

        return values

    def persist_checks(self):
        """
        Persist Soda checks on the file system, if necessary.
        Please note that, if the path already exists, it will be overwritten
        """

        # If a YAML string and path are passed, then persist the configuration
        if self.sodacl_yaml_str and self.sodacl_yaml_path:
            with open(self.sodacl_yaml_path, "w") as f:
                safe_dump(data=self.sodacl_yaml_str, stream=f)