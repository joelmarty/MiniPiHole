from typing import Union, get_type_hints, Literal
from envfileparser import get_env_from_file


class AppConfigError(Exception):
    pass


def _parse_bool(val: Union[str, bool]) -> bool:  # pylint: disable=E1136
    return val if val is bool else val.lower() in ['true', 'yes', '1']


# AppConfig class with required fields, default values, type checking, and typecasting for int and bool values
class AppConfig:
    SCREEN_FLIP: bool = 'false'
    SCREEN_MOCK: bool = 'false'
    SCREEN_COLOR: str = 'yellow'
    PIHOLE_HOST: str = 'localhost'
    PIHOLE_PORT: int = 80
    PIHOLE_CONFDIR: str = '/etc/pihole'
    REFRESH_PERIOD: int = 3600
    LOCALE: str = 'en_US.UTF-8'

    """
    Map environment variables to class fields according to these rules:
      - Field won't be parsed unless it has a type annotation
      - Field will be skipped if not in all caps
      - Class field and environment variable name are the same
    """
    def __init__(self, env):
        for field in self.__annotations__:
            if not field.isupper():
                continue

            # Raise AppConfigError if required field not supplied
            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigError('The {} field is required'.format(field))

            # Cast env var value to expected type and raise AppConfigError on failure
            try:
                var_type = get_type_hints(AppConfig)[field]
                if var_type == bool:
                    value = _parse_bool(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                raise AppConfigError('Unable to cast value of "{}" to type "{}" for "{}" field'.format(
                    env[field],
                    var_type,
                    field
                )
                )

    def __repr__(self):
        return str(self.__dict__)


class PiHoleConfig:
    """
    Retrieve additional config from PiHole own config
    """

    def __init__(self, app_conf: AppConfig):
        self.pihole_vars = f'{app_conf.PIHOLE_CONFDIR}/setupVars.conf'
        self.pihole_iface, self.pihole_token = get_env_from_file('PIHOLE_INTERFACE', 'WEBPASSWORD',
                                                                 file_path=self.pihole_vars)
        self.pihole_api_host = f'{app_conf.PIHOLE_HOST}:{app_conf.PIHOLE_PORT}'
