from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    USE_PROXY_FROM_FILE: bool = False

    REF_ID: str = "MevXkpYU"

    REQUEST_TIMEOUT: list[int] = [30, 60]  
    RETRY_DELAY: list[int] = [3, 10]       
    MAX_RETRIES: int = 5

    ENABLE_QUESTS: bool = True  
    QUEST_CHECK_INTERVAL: list[int] = [300, 900]  
    DELAY_BETWEEN_QUESTS: list[int] = [3, 15]     

    SERVER_CHECK_INTERVAL: list[int] = [240, 360]  
    SERVER_CHECK_TIMEOUT: int = 5     
    MAX_SERVER_CHECK_ATTEMPTS: int = 3
    SERVER_CHECK_RETRY_DELAY: list[int] = [5, 15]  
    SLEEP_ON_SERVER_ERROR: list[int] = [240, 360]  
    SLEEP_AFTER_SESSIONS: list[int] = [18000, 25200]  

    LOGGING_LEVEL: str = "INFO"
    ENABLE_RICH_LOGGING: bool = True
    DETAILED_LOGGING: bool = False  
    LOG_AUTH_DATA: bool = False    
    LOG_RESPONSE_DATA: bool = False 
    LOG_REQUEST_DATA: bool = False   
    LOG_USER_AGENT: bool = True     
    LOG_PROXY: bool = True          

    @property
    def MIN_RETRY_DELAY(self):
        return self.RETRY_DELAY[0]

    @property
    def MAX_RETRY_DELAY(self):
        return self.RETRY_DELAY[1]

    @property
    def MIN_REQUEST_TIMEOUT(self):
        return self.REQUEST_TIMEOUT[0]

    @property
    def MAX_REQUEST_TIMEOUT(self):
        return self.REQUEST_TIMEOUT[1]

    @property
    def MIN_DELAY_BETWEEN_QUESTS(self):
        return self.DELAY_BETWEEN_QUESTS[0]

    @property
    def MAX_DELAY_BETWEEN_QUESTS(self):
        return self.DELAY_BETWEEN_QUESTS[1]

    @property
    def MIN_QUEST_CHECK_INTERVAL(self):
        return self.QUEST_CHECK_INTERVAL[0]

    @property
    def MAX_QUEST_CHECK_INTERVAL(self):
        return self.QUEST_CHECK_INTERVAL[1]

    @property
    def MIN_SERVER_CHECK_INTERVAL(self):
        return self.SERVER_CHECK_INTERVAL[0]

    @property
    def MAX_SERVER_CHECK_INTERVAL(self):
        return self.SERVER_CHECK_INTERVAL[1]

    @property
    def MIN_SERVER_CHECK_RETRY_DELAY(self):
        return self.SERVER_CHECK_RETRY_DELAY[0]

    @property
    def MAX_SERVER_CHECK_RETRY_DELAY(self):
        return self.SERVER_CHECK_RETRY_DELAY[1]

    @property
    def MIN_SLEEP_ON_SERVER_ERROR(self):
        return self.SLEEP_ON_SERVER_ERROR[0]

    @property
    def MAX_SLEEP_ON_SERVER_ERROR(self):
        return self.SLEEP_ON_SERVER_ERROR[1]

    @property
    def MIN_SLEEP_AFTER_SESSIONS(self):
        return self.SLEEP_AFTER_SESSIONS[0]

    @property
    def MAX_SLEEP_AFTER_SESSIONS(self):
        return self.SLEEP_AFTER_SESSIONS[1]


settings = Settings()
