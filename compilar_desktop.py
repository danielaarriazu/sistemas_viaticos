import PyInstaller.__main__

PyInstaller.__main__.run([
    'main_gui.py',
    '--name=Sistema_Viaticos_Armada',
    '--onedir',
    '--noconsole',  
    '--add-data=database.py;.',
    '--add-data=personas.py;.',
    '--add-data=destinos.py;.',
    '--add-data=viaticos.py;.',
    '--add-data=reportes.py;.',

    '--add-data=referencias;referencias',    
    '--hidden-import=reportlab',
    '--hidden-import=reportlab.graphics.barcode',            
    '--hidden-import=sqlite3',               
    '--hidden-import=num2words', 

   '--collect-all=docx',
    '--collect-all=customtkinter',
    '--collect-all=tkcalendar',
    '--collect-all=babel', # tkcalendar necesita babel para los idiomas
    
    '--hidden-import=docx',
    '--hidden-import=customtkinter',
    '--hidden-import=tkcalendar',
    '--noconfirm'
])