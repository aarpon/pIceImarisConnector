# <CustomTools>
#   <Menu>
#    <Item name="pIceImarisConnector: Test Hello World!" icon="Python3" tooltip="Test function for pIceImarisConnector.">
#      <Command>Python3XT::HelloWorldXT(%i)</Command>
#    </Item>
#   </Menu>
# </CustomTools>

from pIceImarisConnector import pIceImarisConnector
import tkinter
import time

def HelloWorldXT(aImarisId):

    # Instantiate an IceImarisConnector object
    conn = pIceImarisConnector(aImarisId)

    # Display version info in a dialog
    top = tkinter.Tk()
    top.title("Hello World!")
    l = tkinter.Label(top,
        text = '... from pIceImarisConnector ' + conn.version +
        ' and ' + conn.mImarisApplication.GetVersion())
    l.pack()
    top.mainloop()

    time.sleep(5)
