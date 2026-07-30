"""
Emergency Response & Spill Containment Playbooks
"""
from typing import Dict, List


class EmergencyPlaybook:
    @staticmethod
    def get_playbook(hazard_type: str) -> Dict:
        playbooks = {
            'amine_spill': {
                'title': 'Amine Chemical Spill Response',
                'ppe': ['Chemical suit', 'Respirator (organic vapor)', 'Neoprene gloves'],
                'actions': [
                    'Evacuate non-essential personnel from immediate area.',
                    'Contain spill using sand or inert absorbent berm.',
                    'Neutralize carefully with dilute citric acid solution.',
                    'Collect in labeled hazardous waste container.',
                ],
                'first_aid': 'Skin contact: Wash with soap/water for 15 min. Eye contact: Flush for 20 min.',
            },
            'gas_leak': {
                'title': 'High-Pressure Gas / CO2 Leak Response',
                'ppe': ['Self-contained breathing apparatus (SCBA)'],
                'actions': [
                    'Sound emergency alarm and evacuate building.',
                    'Isolate gas supply via remote automated emergency shut-off valve (ESDV).',
                    'Ventilate area using explosion-proof exhaust fans.',
                ],
                'first_aid': 'Move victim to fresh air. Provide oxygen if breathing is difficult.',
            },
        }
        return playbooks.get(hazard_type, playbooks['amine_spill'])
