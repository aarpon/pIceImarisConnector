.. toctree::
   :maxdepth: 1

.. _usage:

Usage
=====

In an Imaris XT file:

.. code-block:: python

    # <CustomTools>
    #   <Menu>
    #    <Item name="Hello World!" icon="Python3" tooltip="Hello World from pIceImarisConnector.">
    #      <Command>Python3XT::HelloWorldXT(%i)</Command>
    #    </Item>
    #   </Menu>
    # </CustomTools>

    from pIceImarisConnector import pIceImarisConnector
    import tkinter

    def HelloWorldXT(aImarisId):

        # Instantiate an IceImarisConnector object
        conn = pIceImarisConnector(aImarisId)

        # Display version info in a dialog
        top = tkinter.Tk()
        top.title("Hello World!")
        l = tkinter.Label(top, text=f"... from pIceImarisConnector {conn.__version__} "
                                    f"and {conn.mImarisApplication.GetVersion()}")
        l.pack()
        top.mainloop()

.. note::

    In the call `def HelloWorldXT(aImarisId):`, the argument `aImarisId` can be both an Imaris Application ID as passed by Imaris when running the function from the Imaris Image Processing menu, or an IceImarisConnection object.

From a python console:

.. code-block:: python
    
    # If Imaris is already running

    In [1]: from pIceImarisConnector import pIceImarisConnector

    In [2]: conn = pIceImarisConnector(0)   # 0 is the ID of the running Imaris
    
    In [3]: conn
    Out[3]: pIceImarisConnector: connected to Imaris.

    In[4]: print(conn.mImarisApplication.GetVersion())
    Imaris x64 9.5.1 [Nov 27 2019]

.. code-block:: python

    # If Imaris is not running yet

    In [1]: from pIceImarisConnector import pIceImarisConnector

    In [2]: conn = pIceImarisConnector()
    
    In [3]: conn.startImaris()
    
    # Remember to activate the ImarisXT license!

    In[4]: print(conn.mImarisApplication.GetVersion())
    Imaris x64 9.5.1 [Nov 27 2019]

    In[5]: conn.closeImaris(True)
