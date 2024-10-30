import random
import json
import os
from bot.utils.logger import logger

def generate_android_user_agent():
    android_versions = ['10', '11', '12', '13', '14']
    android_devices = [
        'SM-A515F', 'SM-A526B', 'SM-A536B', 'SM-A546B', 'SM-A736B', 
        'SM-S901B', 'SM-S908B', 'SM-S918B', 'SM-S928B', 'SM-S23U',  
        'SM-F721B', 'SM-F936B', 'SM-F946B',  
        'SM-N986B', 'SM-N981B',  
        'M2101K6G', 'M2102K1G', 'M2012K11G', '2201123G', '2203121C',
        '2201122G', '2201123C', '2211133C', '22041216C', '22041216G',
        'IN2023', 'LE2123', 'NE2213', 'LE2101', 'LE2111', 'LE2115',
        'IN2020', 'IN2010', 'IN2013', 'IN2017', 'IN2019',
        'ASUS_I005D', 'ASUS_I005DA', 'ASUS_I007D', 'ASUS_I003DD', 'ASUS_I006D',
        'Pixel 6', 'Pixel 6 Pro', 'Pixel 7', 'Pixel 7 Pro', 'Pixel 7a',
        'ELS-NX9', 'ELS-N39', 'VOG-L29', 'VOG-L09', 'ANA-NX9',
        'CPH2009', 'CPH2089', 'CPH2119', 'CPH2185', 'CPH2219',
        'V2024', 'V2027', 'V2031', 'V2036', 'V2041',
        'RMX2170', 'RMX2061', 'RMX2176', 'RMX3081', 'RMX3363',
        'XT2201-2', 'XT2175-2', 'XT2137-1', 'XT2101-1', 'XT2125-4',
        'XQ-AT52', 'XQ-AS72', 'XQ-BC72', 'XQ-BQ72', 'XQ-CT72',
        'LM-G900', 'LM-V600', 'LM-G910', 'LM-V500N', 'LM-G850'
    ]
    builds = [
        'MMB29K', 'NRD90M', 'QKQ1.200114.002', 'RKQ1.211119.001', 
        'SKQ1.220519.001', 'TKQ1.220807.001', 'UKQ1.230701.001',
        'SP1A.210812.016', 'TP1A.220624.014', 'TQ3A.230605.012',
        'RQ3A.211001.001', 'SD1A.210817.037', 'RD1A.201105.003.C1',
        'QD4A.200805.003', 'QQ3A.200805.001', 'RP1A.200720.011',
        'SP1A.210812.015', 'TP1A.221005.002', 'TQ2A.230505.002'
    ]
    
    device = random.choice(android_devices)
    android_version = random.choice(android_versions)
    build = random.choice(builds)
    
    chrome_version = f'{random.randint(90, 120)}.0.{random.randint(1000, 9999)}.{random.randint(10, 999)}'
    
    return f'Mozilla/5.0 (Linux; Android {android_version}; {device} Build/{build}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Mobile Safari/537.36'

def load_or_generate_user_agent(session_name: str) -> str:
    ua_file = 'user_agents.json'
    try:
        if os.path.exists(ua_file):
            with open(ua_file, 'r') as f:
                user_agents = json.load(f)
                if session_name in user_agents:
                    logger.info(f"{session_name} | Loaded saved User-Agent")
                    return user_agents[session_name]
        
        user_agent = generate_android_user_agent()
        logger.info(f"{session_name} | Generated new User-Agent")
        
        user_agents = {}
        if os.path.exists(ua_file):
            with open(ua_file, 'r') as f:
                user_agents = json.load(f)
        
        user_agents[session_name] = user_agent
        
        with open(ua_file, 'w') as f:
            json.dump(user_agents, f, indent=4)
            
        return user_agent
                
    except Exception as e:
        logger.error(f"{session_name} | Error working with User-Agent: {e}")
        return generate_android_user_agent()