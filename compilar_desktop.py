import PyInstaller.__main__

PyInstaller.__main__.run([
    'main_gui.py',
    '--name=Sistema_Viaticos_Armada',
    '--onedir',
    '--noconsole',  # <-- Para que no salga la pantalla negra detrás
    '--add-data=database.py;.',
    '--add-data=personas.py;.',
    '--add-data=destinos.py;.',
    '--add-data=viaticos.py;.',
    '--add-data=reportes.py;.',
    '--add-data=referencias;referencias',
    '--hidden-import=babel.numbers', # Necesario para tkcalendar
    '--noconfirm'
])