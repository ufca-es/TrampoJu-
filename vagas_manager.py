# vagas_manager.py
from data_manager import DataManager

class VagasManager:
    def __init__(self, data_manager: DataManager, filename: str):
        self.data_manager = data_manager
        self.filename = filename
        self.vagas = self.data_manager.load_json(self.filename, "vagas")

    def cadastrar_vaga(self, titulo, empresa, local, requisitos, segmento, descricao):
        self.vagas["vagas"].append({
            "titulo": titulo,
            "empresa": empresa,
            "local": local,
            "requisitos": requisitos,
            "segmento": segmento,
            "descricao": descricao
        })
        self.data_manager.save_json(self.filename, self.vagas)

    def buscar_vaga(self, palavra: str) -> list:
        resultados = []
        for vaga in self.vagas["vagas"]:
            texto = f"{vaga.get('titulo','')} {vaga.get('empresa','')} {vaga.get('local','')} {vaga.get('requisitos','')} {vaga.get('segmento','')}".lower()
            if palavra.lower() in texto:
                resultados.append(vaga)
        return resultados

    def listar_vagas(self):
        return self.vagas["vagas"]