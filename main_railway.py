#!/usr/bin/env python3
import os
import requests
from datetime import datetime

class Logger:
    @staticmethod
    def log(msg, level="INFO"):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [{level}] {msg}")

class NoticiasAPI:
    @staticmethod
    def buscar():
        Logger.log("🔍 Buscando notícias...")
        try:
            params = {
                'q': 'vasco futebol',
                'sortBy': 'publishedAt',
                'language': 'pt',
                'pageSize': 5,
                'apiKey': os.getenv('NEWS_API_KEY')
            }
            r = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
            r.raise_for_status()
            articles = r.json().get('articles', [])
            if articles:
                Logger.log(f"✅ Notícia: {articles[0]['title'][:50]}...")
                return articles[0]
        except Exception as e:
            Logger.log(f"❌ Erro: {e}", "ERROR")
        return None

class VascoAI:
    @staticmethod
    def gerar(noticia):
        Logger.log("🤖 Gerando comentário...")
        try:
            titulo = noticia.get('title', '')
            prompt = f"Você é comentarista do Vasco. Comente em 100 palavras sobre: {titulo}"
            headers = {'Authorization': f"Bearer {os.getenv('OPENAI_API_KEY')}", 'Content-Type': 'application/json'}
            payload = {'model': 'gpt-3.5-turbo', 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 150}
            r = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=15)
            r.raise_for_status()
            texto = r.json()['choices'][0]['message']['content']
            Logger.log(f"✅ Comentário: {texto[:50]}...")
            return texto
        except Exception as e:
            Logger.log(f"❌ Erro IA: {e}", "ERROR")
        return None

class InstagramAPI:
    @staticmethod
    def publicar(caption):
        Logger.log("📱 Publicando no Instagram...")
        try:
            url = f"https://graph.instagram.com/{os.getenv('INSTAGRAM_USER_ID', '17841400138')}/media"
            params = {'media_type': 'TEXT', 'text': caption, 'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN')}
            r = requests.post(url, json=params, timeout=15)
            r.raise_for_status()
            media_id = r.json().get('id')
            Logger.log(f"✅ Media criada: {media_id}")
            pub = requests.post(f"https://graph.instagram.com/{media_id}/publish", json={'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN')}, timeout=15)
            pub.raise_for_status()
            Logger.log("✅ Post publicado!")
            return True
        except Exception as e:
            Logger.log(f"❌ Erro Instagram: {e}", "ERROR")
        return False

class VascoBot:
    def executar(self, dry_run=False):
        Logger.log("=" * 50)
        Logger.log("🚀 VASCO BOT INICIADO!")
        Logger.log("=" * 50)
        noticia = NoticiasAPI.buscar()
        if not noticia:
            Logger.log("⚠️ Sem notícia", "WARNING")
            return False
        comentario = VascoAI.gerar(noticia)
        if not comentario:
            Logger.log("⚠️ Erro ao gerar", "WARNING")
            return False
        caption = f"⚫🏴 VASCO DA GAMA ⚫🏴\n\n{comentario}\n\n📰 {noticia.get('source', {}).get('name', 'Fonte')}\n🔗 {noticia.get('url', '')}\n\n#Vasco #VascoGama #CruzMaltina"
        Logger.log(f"📝 Caption: {caption[:100]}...\n")
        if dry_run:
            Logger.log("🧪 TESTE - Nenhum post será publicado")
            Logger.log("✅ Teste OK!")
            return True
        else:
            if InstagramAPI.publicar(caption):
                Logger.log("🎉 BOT EXECUTADO COM SUCESSO!")
                return True
            else:
                Logger.log("❌ Falha ao publicar", "ERROR")
                return False

def main():
    import sys
    dry_run = '--dry-run' in sys.argv or '--test' in sys.argv
    bot = VascoBot()
    bot.executar(dry_run=dry_run)
    Logger.log("=" * 50)
    Logger.log("✅ BOT FINALIZADO")
    Logger.log("=" * 50)

if __name__ == '__main__':
    main()
