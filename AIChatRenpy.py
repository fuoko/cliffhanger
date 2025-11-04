import requests
import json
import os # Ajout de os pour une meilleure gestion des fichiers

# --- Dépendances Simples ---
try:
    from preprompts import PREPROMPTS
except ImportError:
    # Utiliser un dictionnaire de secours si preprompts.py n'existe pas
    PREPROMPTS = {"None": ""}

# ----------------------------------------------------------------------
class AIChat:
    """
    Gère une session de chat multi-tours avec l'API Gemini REST
    en utilisant la librairie 'requests'.
    """
    API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"

    def __init__(
            self,
            name_model="gemini-2.5-flash-lite",
            temperature=1.5,
            top_p=0.95,
            top_k=40,
            max_output_token=8192,
            preprompt_key="None"):
        
        self.api_key = "AIzaSyBwmtH7XJ-8TXshScBrYe5O0cJHlbeEB4c"
            
        self.model_name = name_model
        
        # Le 'generationConfig' utilise le camelCase dans le JSON REST
        self.generation_config = {
            "temperature": temperature,
            "topP": top_p,
            "topK": top_k,
            "maxOutputTokens": max_output_token,
        }
        
        # 2. Gestion du Préprompt et Historique
        self.history = []
        self.preprompt_key = preprompt_key

    def talk(self, user_message: str) -> str:
        """
        Envoie un message à l'API Gemini REST, met à jour l'historique
        et retourne la réponse du modèle.
        """

        contents = self.history + [
            {"role": "user", "parts": [{"text": user_message}]}
        ]
        request_body = {
            "system_instruction":{
                "parts": [
                    {"text": PREPROMPTS.get(self.preprompt_key, "").replace('\n', ' ').strip() }
                ]
            },
            "contents": contents,
            "generationConfig": self.generation_config 
        }
        url = self.API_URL_TEMPLATE.format(self.model_name)
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key} 

        try:
            response = requests.post(url, 
                                     headers=headers, 
                                     params=params, 
                                     data=json.dumps(request_body))
            
            # Lève une exception si le statut n'est pas 2xx (ex: 400 ou 403)
            response.raise_for_status() 

            response_json = response.json()
            
            if not response_json.get('candidates'):
                feedback = response_json.get('promptFeedback', {}).get('blockReason', 'non spécifié')
                return f"Réponse bloquée par l'API (Raison: {feedback})."
            
            model_response_text = response_json['candidates'][0]['content']['parts'][0]['text']

            # Mise à jour de l'historique pour la mémoire
            self.history.append({"role": "user", "parts": [{"text": user_message}]})
            self.history.append({"role": "model", "parts": [{"text": model_response_text}]})
            return model_response_text
        
        except requests.exceptions.HTTPError as err:
            error_details = response.text
            return f"❌ Erreur HTTP {response.status_code}. Détails de l'API: {error_details}"
        except requests.exceptions.RequestException as e:
            return f"⚠️ Erreur de connexion ou de requête: {e}"
