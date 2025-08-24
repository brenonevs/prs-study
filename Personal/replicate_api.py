import os
import pathlib
from typing import Any, BinaryIO, List, Tuple, Union

import dotenv
import replicate

dotenv.load_dotenv()


def _prepare_images(image_sources: List[str]) -> Tuple[List[Union[str, BinaryIO]], List[BinaryIO]]:
    """Normaliza entradas de imagem para a API da Replicate.

    Aceita uma lista de caminhos locais ou URLs. Caminhos existentes são abertos em modo binário
    e retornados como file-like objects; URLs são mantidas como string.

    Args:
      image_sources: Lista de caminhos locais e/ou URLs.

    Returns:
      Uma tupla contendo: (lista normalizada para a API, lista de arquivos abertos que devem ser fechados).
    """
    normalized: List[Union[str, BinaryIO]] = []
    opened_files: List[BinaryIO] = []
    for source in image_sources:
        if os.path.exists(source):
            f = open(source, "rb")
            opened_files.append(f)
            normalized.append(f)
        else:
            normalized.append(source)
    return normalized, opened_files


def run_trellis(images: List[str], *, texture_size: int = 2048, mesh_simplify: float = 0.9,
                generate_model: bool = True, save_gaussian_ply: bool = True,
                ss_sampling_steps: int = 38) -> Any:
    """Executa o modelo firtoz/trellis com uma lista de imagens (paths locais ou URLs).

    Args:
      images: Lista de caminhos locais e/ou URLs para as imagens.
      texture_size: Tamanho da textura gerada.
      mesh_simplify: Fator de simplificação da malha.
      generate_model: Se deve gerar o modelo 3D.
      save_gaussian_ply: Se deve salvar o PLY gaussiano.
      ss_sampling_steps: Passos de amostragem.

    Returns:
      Saída bruta retornada pela API da Replicate (tipicamente dict com FileOutput).
    """
    client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

    normalized, opened = _prepare_images(images)
    try:
        input_payload = {
            "images": normalized,
            "texture_size": texture_size,
            "mesh_simplify": mesh_simplify,
            "generate_model": generate_model,
            "save_gaussian_ply": save_gaussian_ply,
            "ss_sampling_steps": ss_sampling_steps,
        }
        return client.run(
            "firtoz/trellis:e8f6c45206993f297372f5436b90350817bd9b4a0d52d2a76df50c1c8afa2b3c",
            input=input_payload,
        )
    finally:
        for f in opened:
            try:
                f.close()
            except Exception:
                pass


def save_outputs(output: Any, out_dir: str = "outputs") -> None:
    """Salva arquivos de saída retornados pela Replicate, quando aplicável.

    Cria o diretório de saída e grava objetos FileOutput. Ignora chaves com None.
    """
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)

    ext_by_key = {
        "color_video": "mp4",
        "combined_video": "mp4",
        "gaussian_ply": "ply",
        "model_file": "glb",
        "no_background_images": "zip",
        "normal_video": "mp4",
    }

    # Estrutura da saída pode variar entre modelos; aqui tratamos dict e lista.
    if isinstance(output, list):
        for idx, fo in enumerate(output):
            with open(pathlib.Path(out_dir) / f"output_{idx}.bin", "wb") as f:
                f.write(fo.read())
        return

    if isinstance(output, dict):
        for key, value in output.items():
            if value is None:
                continue
            ext = ext_by_key.get(key, "bin")
            with open(pathlib.Path(out_dir) / f"{key}.{ext}", "wb") as f:
                f.write(value.read())


if __name__ == "__main__":
    # Edite esta lista com caminhos locais e/ou URLs.
    images_to_process = [
        rf"C:\Users\breno\Documents\GitHub\prs-gradefy\cloud_functions\images\bolo.png"
        # r"C:\\caminho\\para\\imagem_local.jpg",
    ]

    result = run_trellis(images_to_process)
    print(result)

    # Opcional: salvar saídas em disco
    try:
        save_outputs(result, out_dir="outputs")
        print("Saídas salvas em 'outputs/'.")
    except Exception:
        # Alguns modelos podem não retornar FileOutput; ignore silently.
        pass