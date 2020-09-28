# -*- coding: utf-8 -*-#
#!/usr/bin/env python

import logging
import sys
import decimal

import wx

from mlsrc.mypub import pub, pTopics

class ValBase(wx.PyValidator):
    """Base validator, to transfer data from/to control to the database

    The control using this has to have variables for:

    dbParent
    dbItemName
    dbRelName
    dbColName

    Don't use this directly, but sub-class and implement following methods:

    Clone

    ctrlModified maps to ???
    ctrlGet maps most often to GetValue
    ctrlUpdate maps most often to ChangeValue
    ctrlClear maps most often to ClearValue

    """
    def __init__(self):
        super(ValBase, self).__init__()

    def Clone(self):
        logging.error("Not implement - Clone")

    def ctrlModified(self, flag):
        logging.error("Not implement - ctrlModified")

    def ctrlGet(self):
        logging.error("Not implement - ctrlGet")

    def ctrlUpdate(self, value):
        logging.error("Not implement - ctrlUpdate")

    def ctrlClear(self):
        logging.error("Not implement - ctrlClear")

    def Validate(self, win):
        if hasattr(self.tCtrl, 'IsValid'):
            if self.tCtrl.IsValid():
                return True
            else:
                pub.sendMessage(pTopics.validateControl,
                                dbparent=self.tCtrl.dbParent,
                                ctrl=self.tCtrl)
                return False
        else:
            return True

    def TransferToWindow(self):
        """This gets the data from the db object and writes it to the Window

        If transfer was successful we return True, otherwise an errormsg
        is shown.

        Note if dbItem = None is a request to clear the control
        """
        self.tCtrl = self.GetWindow()
        self.dbItem = getattr(self.tCtrl.dbParent, self.tCtrl.dbItemName)

        if self.dbItem == None:
            self.ctrlClear()
            return True

        try:
            # walk the relations and then get the value from the dbCol
            newAttr = self.dbItem
            if self.tCtrl.dbRelName:
                components = self.tCtrl.dbRelName.split('.')
                for comp in components:
                    # None default can hide an error?!!!??? lets remove it
                    newAttr = getattr(newAttr, comp) #, None)
            if newAttr:
                newAttr = getattr(newAttr, self.tCtrl.dbColName)

            self.ctrlModified(False)
            if newAttr == None:
                self.ctrlClear()
            else:
                tempAttr = newAttr
                self.ctrlUpdate(tempAttr)
                return True

        except KeyError:
            logging.error("Key error for control: %s" % self.tCtrl)
            msg = "dbParent: %s, myLable: %s" % (self.tCtrl.dbParent,
                                                 self.tCtrl.MyLabel)
            logging.exception(msg)
            raise

        except:
            logging.error("error in validator for control: %s" % self.tCtrl)
            msg = "dbParent: %s, myLable: %s" % (self.tCtrl.dbParent,
                                                 self.tCtrl.MyLabel)
            msgDb = "dbColName: %s, dbRelName: %s" % (self.tCtrl.dbColName,
                                                      self.tCtrl.dbRelName)
            logging.error(msg)
            logging.exception(msgDb)
            raise

            self.ctrlClear()
            # there was an error, clear control and let it go on
            return True

    def TransferFromWindow(self):
        """Transfer data from window via the validator to the database.

        Here we write the updated data back to the db.
        """
        self.tCtrl = self.GetWindow()
        self.dbItem = getattr(self.tCtrl.dbParent, self.tCtrl.dbItemName)

        if self.dbItem == None:
            return True

        try:
            if self.tCtrl.IsModified():
                newAttr = self.dbItem
                if self.tCtrl.dbRelName:
                    components = self.tCtrl.dbRelName.split('.')
                    for comp in components:
                        logging.debug('newAttr: %s, comp: %s' % (newAttr,
                                                                 comp))
                        newAttr = getattr(newAttr, comp)

                temp = self.ctrlGet()
                if newAttr:
                    setattr(newAttr, self.tCtrl.dbColName, temp)
                return True

        except:
            logging.error("error in validator for control: %s" % self.tCtrl)
            msg = "dbParent: %s, myLable: %s" % (self.tCtrl.dbParent,
                                                 self.tCtrl.MyLabel)
            msgDb = "dbColName: %s, dbRelName: %s" % (self.tCtrl.dbColName,
                                                      self.tCtrl.dbRelName)
            logging.error(msg)
            logging.exception(msgDb)
            raise


class ValMTC(ValBase):
    """Validator for masked textCtrl"""
    def __init__(self):
        super(ValMTC, self).__init__()

    def Clone(self):
        """Clone function, as the name implies creates a clone of this
        validator for each instance, make sure to pass the appropriate
        parameters.
        """
        return ValMTC()

    def ctrlGet(self):
        return self.tCtrl.GetValue().strip()

    def ctrlModified(self, flag):
        """control handles this internally"""
        pass

    def ctrlUpdate(self, value):
        self.tCtrl.ChangeValue(value.strip())
        self.tCtrl.Refresh()

    def ctrlClear(self):
        self.tCtrl.ClearValueAlt()
        self.tCtrl.Refresh()


class ValMTCNum(ValBase):
    """Validator for Masked NumCtrl"""
    def __init__(self):
        super(ValMTCNum, self).__init__()

    def Clone(self):
        """Clone function, as the name implies creates a clone of this
        validator for each instance, make sure to pass the appropriate
        parameters.
        """
        return ValMTCNum()

    def ctrlGet(self):
        return self.tCtrl.GetValue()

    def ctrlModified(self, flag):
        """control handles this internally"""
        pass

    def ctrlUpdate(self, value):
        if isinstance(value, decimal.Decimal):
            if self.tCtrl.GetFractionWidth() > 0:
                self.tCtrl.ChangeValue(float(value))
                self.tCtrl.Refresh()
            else:
                self.tCtrl.ChangeValue(int(value))
                self.tCtrl.Refresh()
        else:
            if value == None:
                self.tCtrl.ClearValueAlt()
                self.tCtrl.Refresh()
            else:
                self.tCtrl.ChangeValue(str(value))
                self.tCtrl.Refresh()

    def ctrlClear(self):
        self.tCtrl.ClearValueAlt()


class ValMTCVint(ValBase):
    """Validator for Masked NumCtrl for vintage columns"""
    def __init__(self):
        super(ValMTCVint, self).__init__()

    def Clone(self):
        """Clone function, as the name implies creates a clone of this
        validator for each instance, make sure to pass the appropriate
        parameters.
        """
        return ValMTCVint()

    def ctrlGet(self):
        return self.tCtrl.GetValue()

    def ctrlModified(self, flag):
        """control handles this internally"""
        pass

    def ctrlUpdate(self, value):
        if isinstance(value, decimal.Decimal):
            if self.tCtrl.GetFractionWidth() > 0:
                self.tCtrl.ChangeValue(float(value))
                self.tCtrl.Refresh()
            else:
                self.tCtrl.ChangeValue(int(value))
                self.tCtrl.Refresh()
        else:
            if value == None:
                self.tCtrl.ClearValueAlt()
                self.tCtrl.Refresh()
            else:
                self.tCtrl.ChangeValue(str(value))
                self.tCtrl.Refresh()

    def ctrlClear(self):
        self.tCtrl.ClearValueAlt()


class ValTCML(ValBase):
    """Validator for wx.TextCtrl multi line"""
    def __init__(self):
        super(ValTCML, self).__init__()

    def Clone(self):
        """Clone function, as the name implies creates a clone of this
        validator for each instance, make sure to pass the appropriate
        parameters.
        """
        return ValTCML()

    def ctrlGet(self):
        return self.tCtrl.GetValue().strip()

    def ctrlUpdate(self, value):
        self.tCtrl.ChangeValue(value.strip())

    def ctrlModified(self, flag):
        """control handles this internally"""
        pass

    def ctrlClear(self):
        self.tCtrl.ChangeValue("")


class ValTC(ValBase):
    """Validator for plain wx.TextCtrl, e.g. password control"""
    def __init__(self):
        super(ValTC, self).__init__()

    def Clone(self):
        """Clone function, as the name implies creates a clone of this
        validator for each instance, make sure to pass the appropriate
        parameters.
        """
        return ValTC()

    def ctrlGet(self):
        return self.tCtrl.GetValue().strip()

    def ctrlUpdate(self, value):
        self.tCtrl.ChangeValue(value.strip())

    def ctrlModified(self, flag):
        """control handles this internally"""
        pass

    def ctrlClear(self):
        self.tCtrl.ChangeValue("")


class ValCheckB(ValBase):
    """Validator for checkBox control"""
    def __init__(self):
        super(ValCheckB, self).__init__()

    def Clone(self):
        """Clone function, as the name implies creates a clone of this
        validator for each instance, make sure to pass the appropriate
        parameters.
        """
        return ValCheckB()

    def ctrlGet(self):
        return self.tCtrl.GetValue()

    def ctrlUpdate(self, value):
        self.tCtrl.SetValue(value)

    def ctrlModified(self, flag):
        """control handles this internally"""
        pass

    def ctrlClear(self):
        self.tCtrl.SetValue(False)


class ValComboB(ValBase):
    """Validator for checkBox control"""
    def __init__(self):
        super(ValComboB, self).__init__()

    def Clone(self):
        """Clone function, as the name implies creates a clone of this
        validator for each instance, make sure to pass the appropriate
        parameters.
        """
        return ValComboB()

    def ctrlGet(self):
        return self.tCtrl.GetValue()

    def ctrlUpdate(self, value):
        self.tCtrl.SetStringSelection(value.ljust(self.tCtrl._masklength))

    def ctrlModified(self, flag):
        """control handles this internally"""
        pass

    def ctrlClear(self):
        self.tCtrl.SetStringSelection(u'')


class ValSC(ValBase):
    """Validator for search control"""
    def __init__(self):
        super(ValSC, self).__init__()

    def Clone(self):
        """Clone function, as the name implies creates a clone of this
        validator for each instance, make sure to pass the appropriate
        parameters.
        """
        return ValSC()

    def TransferFromWindow(self):
        """The search control is different, instead of setting the column
        we need to set the relevant relation.
        """
        self.tCtrl = self.GetWindow()
        self.dbItem = getattr(self.tCtrl.dbParent, self.tCtrl.dbItemName)

        if self.dbItem == None:
            return True

        try:
            if self.tCtrl.IsModified():
                newAttr = self.dbItem
                if self.tCtrl.dbScRelName:
                    components = self.tCtrl.dbScRelName.split('.')
                    # ignore the last one
                    for comp in components[:-1]:
                        newAttr = getattr(newAttr, comp)

                temp = self.ctrlGet()
                if newAttr:
                    setattr(newAttr, self.tCtrl.dbScFkColName, temp)
                return True

        except:
            logging.error("error in validator for control: %s" % self.tCtrl)
            msg = "dbParent: %s, myLable: %s" % (self.tCtrl.dbParent,
                                                 self.tCtrl.MyLabel)
            msgDb = "dbColName: %s, dbRelName: %s" % (self.tCtrl.dbColName,
                                                      self.tCtrl.dbRelName)
            logging.error(msg)
            logging.exception(msgDb)
            raise

    def ctrlGet(self):
        """this control is a bit special, we need to get the selected
        item
        """
        return self.tCtrl.selectedDbItemPk

    def ctrlUpdate(self, value):
        """this control is a bit special, we ignore value and just
        pass it the approriate dbItem
        """
        # walk the relations and then get the value from the dbCol
        newAttr = self.dbItem
        if self.tCtrl.dbScRelName:
            components = self.tCtrl.dbScRelName.split('.')
            for comp in components:
                if newAttr:
                    newAttr = getattr(newAttr, comp)

        self.tCtrl.doSetDbItem(newAttr)
        self.tCtrl.Refresh()

    def ctrlModified(self, flag):
        self.tCtrl.MarkDirty()

    def ctrlClear(self):
        self.tCtrl.doSetDbItem(None)
        self.tCtrl.Refresh()


class ValEmailTC(ValBase):
    """Validator for email control"""
    def __init__(self):
        super(ValEmailTC, self).__init__()

    def Clone(self):
        """Clone function, as the name implies creates a clone of this
        validator for each instance, make sure to pass the appropriate
        parameters.
        """
        return ValEmailTC()

    def ctrlGet(self):
        logging.debug(self.tCtrl.getTc().GetValue().strip())
        return self.tCtrl.getTc().GetValue().strip()

    def ctrlModified(self, flag):
        """control handles this internally"""
        pass

    def ctrlUpdate(self, value):
        self.tCtrl.getTc().ChangeValue(value.strip())
        self.tCtrl._hasData = True
        self.tCtrl.getTc().Refresh()

    def ctrlClear(self):
        self.tCtrl.getTc().ClearValueAlt()
        self.tCtrl._hasData = False
        self.tCtrl.getTc().Refresh()

