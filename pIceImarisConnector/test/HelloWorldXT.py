# <CustomTools>
#   <Menu>
#    <Item name="pIceImarisConnector: Test Hello World!" icon="Python3" tooltip="Test function for pIceImarisConnector.">
#      <Command>Python3XT::HelloWorldXT(%i)</Command>
#    </Item>
#   </Menu>
# </CustomTools>

import tkinter

from pIceImarisConnector import pIceImarisConnector


def HelloWorldXT(aImarisId):

    # Instantiate an IceImarisConnector object
    conn = pIceImarisConnector(aImarisId)

    # Display version info in a dialog
    top = tkinter.Tk()
    top.title("Hello World!")
    l = tkinter.Label(
        top,
        text=f"... from pIceImarisConnector {conn.__version__} "
        f"and {conn.mImarisApplication.GetVersion()}",
    )
    l.pack()
    top.mainloop()
