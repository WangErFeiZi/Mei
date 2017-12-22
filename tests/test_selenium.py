import unittest, re, json, threading
from base64 import b64encode
from selenium import webdriver
from app import create_app, db
from app.models import User, Role, Post
from flask import url_for


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        try:
            cls.client = webdriver.Chrome(chrome_options=options)
        except:
            pass
        if cls.client:
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.pist()

            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            admin_role = Role.query.filter_by(permission=0xff).first()
            admin = User(email='john@example.com',
                         username='john', password='cat',
                         role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            cls.server_thread = threading.Thread(target=cls.app.run)
            cls.server_thread.start()
            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            db.drop_all()
            db.session.remove()

            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s+Stranger!', self.client.page_source))

        self.client.find_element_by_link_text('登陆').click()
        self.assertTrue('<h1>登陆</h1>' in self.client.page_source)

        self.client.find_element_by_name('email').send_keys('john@exmaple.com')
        self.client.find_element_by_name('password').send_keys('cat')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search('Hello,\s+john!', self.client.page_source))

        self.client.find_element_by_link_text('个人资料').click()
        self.assertTrue('<h1>john</h1>' in self.client.page_source)

