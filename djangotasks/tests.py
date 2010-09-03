#
# Copyright (c) 2010 by nexB, Inc. http://www.nexb.com/ - All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#    
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
# 
#     3. Neither the names of Django, nexB, Django-tasks nor the names of the contributors may be used
#        to endorse or promote products derived from this software without
#        specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import with_statement 

import sys
import StringIO
import os
import unittest
import tempfile
import time
import inspect
from os.path import join, dirname, basename, exists, join

import re
DATETIME_REGEX = re.compile('[a-zA-Z]+ \d+\, \d\d\d\d at \d+(\:\d+)? [ap]\.m\.')

from models import Task, TaskManager

class StandardOutputCheck(object):
    def __init__(self, test, expected_stdout = None, fail_if_different=True):
        self.test = test
        self.expected_stdout = expected_stdout or ''
        self.fail_if_different = fail_if_different
        
    def __enter__(self):
        self.stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
        
    def __exit__(self, type, value, traceback):
        # Restore state
        self.stdoutvalue = sys.stdout.getvalue()
        sys.stdout = self.stdout

        # Check the output only if no exception occured (to avoid "eating" test failures)
        if type:
            return
        
        if self.fail_if_different:
            self.test.assertEquals(self.expected_stdout, self.stdoutvalue)

class TestModel(object):
    ''' A mock Model object for task tests'''
    class Manager(object):
        def get(self, pk):
            if basename(pk) not in ['key1', 'key2', 'key3', 'key with space', 'key-more']:
                raise Exception("Not a good object loaded")
            return TestModel(pk)

    objects = Manager()
    def __init__(self, pk):
        self.pk = pk

    def run_something_long(self, msg=''):
        print "running something..."
        sys.stdout.flush()
        self._trigger("run_something_long_1")
        time.sleep(0.2)
        print "still running..."
        sys.stdout.flush()
        time.sleep(0.2)
        self._trigger("run_something_long_2")
        return "finished"
    
    def run_something_else(self):
        pass

    def run_something_failing(self):
        print "running, will fail..."
        sys.stdout.flush()
        time.sleep(0.2)
        self._trigger("run_something_failing")
        raise Exception("Failed !")

    def run_something_with_required(self):
        print "running required..."
        sys.stdout.flush()
        time.sleep(0.2)
        self._trigger("run_something_with_required")
        return "finished required"

    def run_something_with_required_failing(self):
        print "running required..."
        sys.stdout.flush()
        time.sleep(0.2)
        self._trigger("run_something_with_required")
        return "finished required"

    def run_something_with_two_required(self):
        # not called in the tests
        pass

    def run_a_method_that_is_not_registered(self):
        # not called in the tests
        pass

    def run_something_fast(self):
        print "Doing something fast"
        time.sleep(0.1)
        self._trigger("run_something_fast")

    def check_database_settings(self):
        from django.db import connection
        print connection.settings_dict["NAME"]
        time.sleep(0.1)
        self._trigger("check_database_settings")

    def _trigger(self, event):
        open(self.pk + event, 'w').writelines(["."])
        
class ViewsTestCase(unittest.TestCase):
    def failUnlessRaises(self, excClassOrInstance, callableObj, *args, **kwargs):
        # improved method compared to unittest.TestCase.failUnlessRaises:
        # also check the content of the exception
        if inspect.isclass(excClassOrInstance):
            return unittest.TestCase.failUnlessRaises(self, excClassOrInstance, callableObj, *args, **kwargs)

        excClass = excClassOrInstance.__class__
        try:
            callableObj(*args, **kwargs)
        except excClass, e:
            self.assertEquals(str(excClassOrInstance), str(e))
        else:
            if hasattr(excClass,'__name__'): excName = excClass.__name__
            else: excName = str(excClass)
            raise self.failureException, "%s not raised" % excName

    assertRaises = failUnlessRaises

    def setUp(self):
        TaskManager.DEFINED_TASKS['djangotasks.tests.TestModel'] = \
            [('run_something_long', "Run a successful task", ''),
             ('run_something_else', "Run an empty task", ''),
             ('run_something_failing', "Run a failing task", ''),
             ('run_something_with_required', "Run a task with a required task", 'run_something_long'),
             ('run_something_with_two_required', "Run a task with two required task", 'run_something_long,run_something_with_required'),
             ('run_something_fast', "Run a fast task", ''),
             ('run_something_with_required_failing', "Run a task with a required task that fails", 'run_something_failing'),
             ('check_database_settings', "Checks the database settings", ''),
             ]
        import tempfile
        self.tempdir = tempfile.mkdtemp()
        import os
        os.environ['DJANGOTASKS_TESTING'] = "YES"

    def tearDown(self):
        del TaskManager.DEFINED_TASKS['djangotasks.tests.TestModel']
        for task in Task.objects.filter(model='djangotasks.tests.TestModel'):
            task.delete()
        import shutil
        shutil.rmtree(self.tempdir)
        import os
        del os.environ['DJANGOTASKS_TESTING']

    def test_tasks_import(self):
        from djangotasks.models import _my_import
        self.assertEquals(TestModel, _my_import('djangotasks.tests.TestModel'))

    def _create_task(self, method, object_id):
        from djangotasks.models import _qualified_class_name
        return Task.objects._create_task(_qualified_class_name(method.im_class), 
                                         method.im_func.__name__, 
                                         object_id)


    def test_tasks_invalid_method(self):
        self.assertRaises(Exception("Method 'run_a_method_that_is_not_registered' not registered for model 'djangotasks.tests.TestModel'"), 
                          self._create_task, TestModel.run_a_method_that_is_not_registered, 'key1')

        class NotAValidModel(object):
            def a_method(self):
                pass
        self.assertRaises(Exception("'module' object has no attribute 'NotAValidModel'"), 
                          self._create_task, NotAValidModel.a_method, 'key1')
            
        self.assertRaises(Exception("Not a good object loaded"), 
                          self._create_task, TestModel.run_something_long, 'key_that_does_not_exist')

    def test_tasks_register(self):
        class MyClass(object):
            def mymethod1(self):
                pass

            def mymethod2(self):
                pass
            
            def mymethod3(self):
                pass
                
                
        from djangotasks.models import register_task
        try:
            register_task(MyClass.mymethod3, None, MyClass.mymethod1, MyClass.mymethod2)
            register_task(MyClass.mymethod1, '''Some documentation''', MyClass.mymethod2)
            register_task(MyClass.mymethod2, '''Some other documentation''')
            self.assertEquals([('mymethod3', '', 'mymethod1,mymethod2'),
                               ('mymethod1', 'Some documentation', 'mymethod2'),
                               ('mymethod2', 'Some other documentation', '')],
                              TaskManager.DEFINED_TASKS['djangotasks.tests.MyClass'])
        finally:
            del TaskManager.DEFINED_TASKS['djangotasks.tests.MyClass']

    def _wait_until(self, key, event):
        max = 50 # 5 seconds max
        while not exists(join(self.tempdir, key + event)) and max:
            time.sleep(0.1)
            max -= 1
        if not max:
            self.fail("Timeout")
        
    def _reset(self, key, event):
        os.remove(join(self.tempdir, key + event))

    def _assert_status(self, expected_status, task):
        task = Task.objects.get(pk=task.pk)
        self.assertEquals(expected_status, task.status)

    def test_tasks_run_successful(self):
        task = self._create_task(TestModel.run_something_long, join(self.tempdir, 'key1'))
        Task.objects.run_task(task.pk)
        with StandardOutputCheck(self, "Starting task " + str(task.pk) + "... started.\n"):
            Task.objects._do_schedule()
        self._wait_until('key1', 'run_something_long_2')
        time.sleep(0.5)
        new_task = Task.objects.get(pk=task.pk)
        self.assertEquals(u'running something...\nstill running...\n'
                          , new_task.log)
        self.assertEquals("successful", new_task.status)

    def test_tasks_run_check_database(self):
        task = self._create_task(TestModel.check_database_settings, join(self.tempdir, 'key1'))
        Task.objects.run_task(task.pk)
        with StandardOutputCheck(self, "Starting task " + str(task.pk) + "... started.\n"):
            Task.objects._do_schedule()
        self._wait_until('key1', 'check_database_settings')
        time.sleep(0.5)
        new_task = Task.objects.get(pk=task.pk)
        from django.db import connection
        self.assertEquals(connection.settings_dict["NAME"] + u'\n' , new_task.log) # May fail if your Django settings define a different test database for each run: in which case you should modify it, to ensure it's always the same.
        self.assertEquals("successful", new_task.status)

    def test_tasks_run_with_space_fast(self):
        task = self._create_task(TestModel.run_something_fast, join(self.tempdir, 'key with space'))
        Task.objects.run_task(task.pk)
        with StandardOutputCheck(self, "Starting task " + str(task.pk) + "... started.\n"):
            Task.objects._do_schedule()
        self._wait_until('key with space', "run_something_fast")
        time.sleep(0.5)
        new_task = Task.objects.get(pk=task.pk)
        self.assertEquals(u'Doing something fast\n'
                          , new_task.log)
        self.assertEquals("successful", new_task.status)

    def test_tasks_run_cancel_running(self):
        task = self._create_task(TestModel.run_something_long, join(self.tempdir, 'key1'))
        Task.objects.run_task(task.pk)
        with StandardOutputCheck(self, "Starting task " + str(task.pk) + "... started.\n"):
            Task.objects._do_schedule()
        self._wait_until('key1', "run_something_long_1")
        Task.objects.cancel_task(task.pk)
        output_check = StandardOutputCheck(self, fail_if_different=False)
        with output_check:
            Task.objects._do_schedule()
            time.sleep(0.3)
        self.assertTrue(("Cancelling task " + str(task.pk) + "...") in output_check.stdoutvalue)
        self.assertTrue("cancelled.\n" in output_check.stdoutvalue)
        #self.assertTrue('INFO: failed to mark tasked as finished, from status "running" to "unsuccessful" for task 3. May have been finished in a different thread already.\n'
        #                in output_check.stdoutvalue)

        new_task = Task.objects.get(pk=task.pk)
        self.assertEquals("cancelled", new_task.status)
        self.assertTrue(u'running something...' in new_task.log)
        self.assertFalse(u'still running...' in new_task.log)
        self.assertFalse('finished' in new_task.log)

    def test_tasks_run_cancel_scheduled(self):
        task = self._create_task(TestModel.run_something_long, join(self.tempdir, 'key1'))
        with StandardOutputCheck(self):
            Task.objects._do_schedule()
        Task.objects.run_task(task.pk)
        Task.objects.cancel_task(task.pk)
        with StandardOutputCheck(self, "Cancelling task " + str(task.pk) + "... cancelled.\n"):
            Task.objects._do_schedule()
        new_task = Task.objects.get(pk=task.pk)
        self.assertEquals("cancelled", new_task.status)            
        self.assertEquals("", new_task.log)

    def test_tasks_run_failing(self):
        task = self._create_task(TestModel.run_something_failing, join(self.tempdir, 'key1'))
        Task.objects.run_task(task.pk)
        with StandardOutputCheck(self, "Starting task " + str(task.pk) + "... started.\n"):
            Task.objects._do_schedule()
        self._wait_until('key1', "run_something_failing")
        time.sleep(0.5)
        new_task = Task.objects.get(pk=task.pk)
        self.assertEquals("unsuccessful", new_task.status)
        self.assertTrue(u'running, will fail...' in new_task.log)
        self.assertTrue(u'raise Exception("Failed !")' in new_task.log)
        self.assertTrue(u'Exception: Failed !' in new_task.log)
    
    def test_tasks_get_tasks_for_object(self):
        tasks = Task.objects.tasks_for_object(TestModel, 'key2')
        self.assertEquals(8, len(tasks))
        self.assertEquals('defined', tasks[0].status)
        self.assertEquals('defined', tasks[1].status)
        self.assertEquals('run_something_long', tasks[0].method)
        self.assertEquals('run_something_else', tasks[1].method)

    def test_tasks_get_task_for_object(self):
        self.assertRaises(Exception("Method 'run_doesn_not_exists' not registered for model 'djangotasks.tests.TestModel'"), 
                          Task.objects.task_for_object, TestModel, 'key2', 'run_doesn_not_exists')
        task = Task.objects.task_for_object(TestModel, 'key2', 'run_something_long')
        self.assertEquals('defined', task.status)
        self.assertEquals('run_something_long', task.method)

    def test_tasks_get_task_for_object_required(self):
        task = Task.objects.task_for_object(TestModel, 'key-more', 'run_something_with_two_required')
        self.assertEquals('run_something_long,run_something_with_required', task.required_methods)
        
    def test_tasks_archive_task(self):
        tasks = Task.objects.tasks_for_object(TestModel, 'key3')
        task = tasks[0]
        self.assertTrue(task.pk)
        task.status = 'successful'
        task.save()
        self.assertEquals(False, task.archived)
        new_task = self._create_task(TestModel.run_something_long,
                                     'key3')
        self.assertTrue(new_task.pk)
        self.assertTrue(task.pk != new_task.pk)
        old_task = Task.objects.get(pk=task.pk)        
        self.assertEquals(True, old_task.archived, "Task should have been archived once a new one has been created")

    def test_tasks_get_required_tasks(self):
        task = self._create_task(TestModel.run_something_with_required, 'key1')
        self.assertEquals(['run_something_long'],
                          [required_task.method for required_task in task.get_required_tasks()])
        
        
        task = self._create_task(TestModel.run_something_with_two_required, 'key1')
        self.assertEquals(['run_something_long', 'run_something_with_required'],
                          [required_task.method for required_task in task.get_required_tasks()])

    def test_tasks_run_required_task_successful(self):
        required_task = Task.objects.task_for_object(TestModel, join(self.tempdir, 'key1'), 'run_something_long')
        task = self._create_task(TestModel.run_something_with_required, join(self.tempdir, 'key1'))
        self.assertEquals("defined", required_task.status)

        Task.objects.run_task(task.pk)
        self._assert_status("scheduled", task)
        self._assert_status("scheduled", required_task)

        with StandardOutputCheck(self, "Starting task " + str(required_task.pk) + "... started.\n"):
            Task.objects._do_schedule()
        time.sleep(0.5)
        self._assert_status("scheduled", task)
        self._assert_status("running", required_task)

        self._wait_until('key1', 'run_something_long_2')
        time.sleep(0.5)
        self._assert_status("scheduled", task)
        self._assert_status("successful", required_task)

        with StandardOutputCheck(self, "Starting task " + str(task.pk) + "... started.\n"):
            Task.objects._do_schedule()
        time.sleep(0.5)
        self._assert_status("running", task)
        self._assert_status("successful", required_task)
        self._wait_until('key1', "run_something_with_required")
        time.sleep(0.5)
        self._assert_status("successful", task)
        task = Task.objects.get(pk=task.pk)
        complete_log, _ = DATETIME_REGEX.subn('', task.complete_log())

        self.assertEquals(u'Run a successful task started on \nrunning something...\nstill running...\n\n' +
                          u'Run a successful task finished successfully on \n' + 
                          u'Run a task with a required task started on \nrunning required...\n\n' + 
                          u'Run a task with a required task finished successfully on ', complete_log)

    def test_tasks_run_required_task_failing(self):
        required_task = Task.objects.task_for_object(TestModel, join(self.tempdir, 'key1'), 'run_something_failing')
        task = self._create_task(TestModel.run_something_with_required_failing, join(self.tempdir, 'key1'))
        self.assertEquals("defined", required_task.status)

        Task.objects.run_task(task.pk)
        self._assert_status("scheduled", task)
        self._assert_status("scheduled", required_task)

        with StandardOutputCheck(self, "Starting task " + str(required_task.pk) + "... started.\n"):
            Task.objects._do_schedule()
        time.sleep(0.5)
        self._assert_status("scheduled", task)
        self._assert_status("running", required_task)

        self._wait_until('key1', 'run_something_failing')
        time.sleep(0.5)
        self._assert_status("scheduled", task)
        self._assert_status("unsuccessful", required_task)

        with StandardOutputCheck(self):
            Task.objects._do_schedule()
        time.sleep(0.5)
        self._assert_status("unsuccessful", task)
        task = Task.objects.get(pk=task.pk)

        complete_log, _ = DATETIME_REGEX.subn('', task.complete_log())
        self.assertTrue(complete_log.startswith('Run a failing task started on \nrunning, will fail...\nTraceback (most recent call last):'))
        self.assertTrue(complete_log.endswith(u', in run_something_failing\n    raise Exception("Failed !")\nException: Failed !\n\n' + 
                                              u'Run a failing task finished with error on \n' + 
                                              u'Run a task with a required task that fails started\n' + 
                                              u'Run a task with a required task that fails finished with error'))
        self.assertEquals("unsuccessful", task.status)

    def test_tasks_run_again(self):
        tasks = Task.objects.tasks_for_object(TestModel, join(self.tempdir, 'key1'))
        task = tasks[5]
        self.assertEquals('run_something_fast', task.method)
        Task.objects.run_task(task.pk)
        with StandardOutputCheck(self, "Starting task " + str(task.pk) + "... started.\n"):
            Task.objects._do_schedule()
        self._wait_until('key1', "run_something_fast")
        time.sleep(0.5)
        self._reset('key1', "run_something_fast")
        self._assert_status("successful", task)
        Task.objects.run_task(task.pk)
        output_check = StandardOutputCheck(self, fail_if_different=False)
        with output_check:
            Task.objects._do_schedule()
        self._wait_until('key1', "run_something_fast")
        time.sleep(0.5)
        import re
        pks = re.findall(r'(\d+)', output_check.stdoutvalue)
        self.assertEquals(1, len(pks))
        self.assertEquals("Starting task " + pks[0] + "... started.\n", output_check.stdoutvalue)
        new_task = Task.objects.get(pk=int(pks[0]))
        self.assertTrue(new_task.pk != task.pk)
        self.assertEquals("successful", new_task.status)
        tasks = Task.objects.tasks_for_object(TestModel, join(self.tempdir, 'key1'))
        self.assertEquals(new_task.pk, tasks[5].pk)
        

    def NOtest_tasks_exception_in_thread(self):
        task = self._create_task(TestModel.run_something_long, join(self.tempdir, 'key1'))
        Task.objects.run_task(task.pk)
        task = self._create_task(TestModel.run_something_long, join(self.tempdir, 'key1'))
        task_delete = self._create_task(TestModel.run_something_long, join(self.tempdir, 'key1'))
        task_delete.delete()
        try:
            Task.objects.get(pk=task.pk)
            self.fail("Should throw an exception")
        except Exception, e:
            self.assertEquals("Task matching query does not exist.", str(e))
            
        output_check = StandardOutputCheck(self, fail_if_different=False)
        with output_check:
            task.do_run()
            time.sleep(0.5)
        self.assertTrue("Exception: Failed to mark task with " in output_check.stdoutvalue)
        self.assertTrue("as started, task does not exist" in output_check.stdoutvalue)
        self.assertTrue('INFO: failed to mark tasked as finished, from status "running" to "unsuccessful" for task' in output_check.stdoutvalue)
