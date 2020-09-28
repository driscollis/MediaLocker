# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""Setup pubsub, note that the valid topics have
to be defined in mypub_topics and you then use it
as shown in the following within the application

Note that the following expects a very recent copy of
pubsub, it is supplied with wxPython 2.9.3 or is also
available from the wxPython or pubsub repos

    from mypub import pub, pTopics

    # to subscribe
    pub.subscribe(listenerFn, pTopics.statusText)
    pub.subscribe(listenerFn2, pTopics.data.commitDone)
    # see below for some more samples

    # to notify
    pub.sendMessage(pTopics.data.commitDone, dbparent=someparent)
    pub.sendMessage(pTopics.statusText, msg='some text')


    # see below for some more samples

"""
__all__ = ['pub', 'pTopics']

import logging

import wx.lib.pubsub.setupkwargs
from wx.lib.pubsub import pub

import mlsrc.mypub_topics as pTopics

pub.importTopicTree(pTopics, format=pub.TOPIC_TREE_FROM_CLASS)
pub.setTopicUnspecifiedFatal()

if __name__ == u'__main__':
    logging.info("pubsub version: %s" % pub.VERSION_STR)

    class Listener:
        def onTopic11(self, msg, msg2, extra=None):
            print 'Method Listener.onTopic11 received: ', `msg`, `msg2`, `extra`

        def onTopic1(self, msg, topic=pub.AUTO_TOPIC):
            info = 'Method Listener.onTopic1 received "%s" message: %s'
            print info % (topic.getName(), `msg`)

        def __call__(self, **kwargs):
            print 'Listener instance received: ', kwargs

    listenerObj = Listener()


    def listenerFn(msg, msg2, extra=None):
        print 'Function listenerFn received: ', `msg`, `msg2`, `extra`


    def init():
        '''Do something that changes topic tree so exportTopicTree interesting'''

        def proto(msg, arg1=None): pass
        topic = pub.getOrCreateTopic('topic_2.subtopic_21', proto)
        topic.setDescription( 'description for subtopic 21')

    init()

    pub.subscribe(listenerObj, pub.ALL_TOPICS) # via its __call__

    pub.subscribe(listenerFn, 'topic_1.subtopic_11')
    pub.subscribe(listenerObj.onTopic11, 'topic_1.subtopic_11')

    pub.subscribe(listenerObj.onTopic1, 'topic_1')

    # send something
    pub.sendMessage('topic_1', msg='message for topic 1')
    pub.sendMessage('topic_2.subtopic_21', msg='message for subtopic 2')

    def listenerTest(msg, flag=False):
        print msg

    def listenerTest2(msg, flag=False):
        print msg

    def listenerTest3(dbparent=None):
        print dbparent

    # would be nice if this would work
    pub.subscribe(listenerTest, pTopics.statusText)
    pub.subscribe(listenerTest2, pTopics.statusText)
    pub.sendMessage(pTopics.statusText, msg='message for statusText',
                                            flag='something')
    pub.subscribe(listenerTest3, pTopics.data.needsSaving)
    pub.subscribe(listenerTest3, pTopics.data.commitDone)
    pub.sendMessage(pTopics.data.commitDone, dbparent='someone')
    pub.sendMessage(pTopics.data.needsSaving, dbparent='someone2')
