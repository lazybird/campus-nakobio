import os, json, re, time, requests

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "anthropic/claude-sonnet-4.5"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

SYS_PROMPT = """Tu es un expert traducteur en Mandingue/Bamanankan et écriture N'ko (ߒߞߏ - Unicode U+07C0 à U+07FF) pour le Campus Nakôbio.
Tu traduis en Bamanankan avec écriture N'ko.
Vocabulaire :
- Sol vivant = ߘߎ߰ߞߟߏ ߓߊߟߏߣߍ߲
- Bio-intensif = ߛߣߍ߬ߞߍ ߓߌ߬ߟߊ߬ߢߐ߲߰ߡߊ
- Planches de culture permanentes = ߛߍ߬ߣߍ ߟߊ߬ߘߊ߲߬ߠߌ߲ ߓߟߐߞߐ
- Passe-pieds = ߕߊ߯ߡߊߟߌ ߛߌߟߊ
- Compost = ߞߏ߲ߔߏߛߌߕߌ (ߝߍߘߍ߲ߝߋ߲ ߣߐ߰)
- Irrigation douce et globale = ߖߌ ߟߊߓߏ߬ߦߊ߬ߟߌ ߡߢߊߣߍ߲ ߊ߬ ߣߌ߫ ߓߍ߯ߦߊߡߊ
Réponds STRICTEMENT par un JSON valide avec {"pages": [{"page_number": 11, "title": "...", "text": "..."}, ...]}.
"""

with open('src/data/maraichage/101_fondamentaux_maraichage_sol_vivant.json') as f:
    fr_data = json.load(f)

pages_to_translate = fr_data['pages'][10:30]
items_fr = [{"page_number": p["page_number"], "title": p["title"], "text": p["text"]} for p in pages_to_translate]

user_prompt = f"Traduis ces 20 diapositives pédagogiques maraîchères du français vers l'écriture N'ko (ߒߞߏ):\n\n{json.dumps(items_fr, ensure_ascii=False, indent=2)}\n\nRetourne STRICTEMENT le JSON demandé."

print("Envoi de la requête à Claude Sonnet 4.5...", flush=True)
payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": SYS_PROMPT},
        {"role": "user", "content": user_prompt}
    ],
    "temperature": 0.15
}
r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)
if r.status_code == 200:
    content = r.json()["choices"][0]["message"]["content"]
    m = re.search(r"\{[\s\S]*\}", content)
    if m:
        res = json.loads(m.group(0), strict=False)
        translated_pages = res.get("pages", [])
        print(f"Reçu {len(translated_pages)} pages traduites en N'ko !", flush=True)
        
        with open('src/data/maraichage/101_fondamentaux_maraichage_sol_vivant.bm-nko.json', 'r') as f_nko:
            nko_data = json.load(f_nko)
            
        trans_dict = {p["page_number"]: p for p in translated_pages}
        for p in nko_data["pages"]:
            num = p["page_number"]
            if num in trans_dict:
                p["title"] = trans_dict[num]["title"]
                p["text"] = trans_dict[num]["text"]
                print(f"✓ P{num} mis à jour en N'ko: {p['title'][:40]}")
                
        with open('src/data/maraichage/101_fondamentaux_maraichage_sol_vivant.bm-nko.json', 'w') as f_nko:
            json.dump(nko_data, f_nko, ensure_ascii=False, indent=2)
            
        print("Sauvegarde terminée avec succès !")
    else:
        print("Erreur Regex JSON")
else:
    print(f"Erreur API: {r.status_code} - {r.text[:200]}")
