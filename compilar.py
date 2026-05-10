import PyInstaller.__main__

PyInstaller.__main__.run([
    'main_gui.py',                           
    '--name=Sistema_Viaticos_Armada',        
    '--onedir', 
    '--noconsole',                           # <-- Oculta la consola negra de fondo
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
    '--hidden-import=babel.numbers',         # <-- Necesario para el nuevo calendario
    '--noconfirm'                            
])