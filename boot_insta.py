# postar_story_simples.py
from instagrapi import Client
import os


def postar_story_agora(caminho_imagem):
    """Função única para postar story"""
    
    # Verifica se a imagem existe
    if not os.path.exists(caminho_imagem):
        print(f"❌ Imagem não encontrada: {caminho_imagem}")
        return False
    
    print(f"📤 Postando: {caminho_imagem}")
    
    try:
        # Login
        client = Client()
        client.login(
            "lamarcamarao",
            'pesadelolost1'
        )
        
        # Posta story
        client.photo_upload_to_story(caminho_imagem)
        print("✅ Story postado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

# ⚠️ COLOQUE O CAMINHO DA SUA IMAGEM AQUI ⚠️
minha_imagem = r"C:\Users\ailto\Downloads\WhatsApp Image 2025-11-08 at 8.39.29 AM.jpeg"

if __name__ == "__main__":
    postar_story_agora(minha_imagem)