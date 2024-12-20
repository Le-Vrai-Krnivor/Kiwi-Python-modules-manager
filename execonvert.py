import os
import subprocess
import sys
import shutil

def create_spec_file(main_path, icon_path=None):
    main_path_escaped = repr(main_path.replace('\\', '\\\\'))
    if icon_path:
        icon_path_escaped = repr(icon_path.replace('\\', '\\\\'))
    else:
        icon_path_escaped = 'None'

    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None
a = Analysis(
    [{main_path_escaped}],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'numpy', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Kiwi-Python-Modules-Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={icon_path_escaped},
)
"""
    
    with open("Kiwi-Python-Modules-Manager.spec", "w") as spec_file:
        spec_file.write(spec_content)
    
    print("Fichier .spec créé avec succès.")

def cleanup():
    for item in ['build', 'dist', '__pycache__', 'Kiwi-Python-Modules-Manager.spec']:
        if os.path.isdir(item):
            shutil.rmtree(item)
        elif os.path.isfile(item):
            os.remove(item)
    
    print("Nettoyage terminé.")

def create_executable():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_path = os.path.join(script_dir, "main.py")

    if not os.path.exists(main_path):
        print(f"Erreur : Le fichier main.py n'a pas été trouvé dans {script_dir}")
        return False

    if os.path.exists("Kiwi-Python-Modules-Manager.exe"):
        print("L'exécutable Kiwi-Python-Modules-Manager.exe existe déjà.")
        return False

    # Demande à l'utilisateur s'il veut ajouter une icône
    add_icon = input("Voulez-vous ajouter une icône ? (oui/non) : ").strip().lower()
    
    icon_path = None
    if add_icon == 'oui':
        icon_name = input("Veuillez entrer le nom du fichier d'icône (avec l'extension .ico) : ").strip()
        icon_path = os.path.join(script_dir, icon_name)
        
        if not os.path.exists(icon_path):
            print(f"Erreur : Le fichier d'icône '{icon_name}' n'a pas été trouvé dans {script_dir}.")
            return False

    try:
        create_spec_file(main_path, icon_path)
        subprocess.run(["pyinstaller", "Kiwi-Python-Modules-Manager.spec"], check=True)

        exe_path = os.path.join("dist", "Kiwi-Python-Modules-Manager.exe")
        if os.path.exists(exe_path):
            shutil.move(exe_path, "Kiwi-Python-Modules-Manager.exe")
            print("Exécutable créé avec succès!")
            cleanup()
            return True
        else:
            print("Erreur : L'exécutable n'a pas été trouvé après la compilation.")
    
    except subprocess.CalledProcessError:
        print("Erreur lors de la création de l'exécutable.")
    
    except FileNotFoundError:
        print("PyInstaller n'est pas installé. Veuillez l'installer avec 'pip install pyinstaller'.")
    
    return False

if __name__ == "__main__":
    create_executable()
