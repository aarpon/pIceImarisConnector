# Hello World! XT example
#
# <CustomTools>
#  <Menu>
#   <Submenu name="ImarisXT course">
#    <Item name="Hello World!" icon="Python">
#   <Command>PythonXT::HelloWorldXT(#i)</Command>
#  </Item>
# </Submenu>
# </Menu>
# </CustomTools>

from pIceImarisConnector import pIceImarisConnector
import Tkinter

def HelloWorldXT(aImarisId):

    # Instantiate an IceImarisConnector object
    conn = pIceImarisConnector(aImarisId)

    # Display version info in a dialog
    top = Tkinter.Tk()
    top.title("Hello World!")
    l = Tkinter.Label(top,
        text = '... from pIceImarisConnector ' + conn.version +
        ' and ' + conn.mImarisApplication.GetVersion())
    l.pack()
    top.mainloop()
