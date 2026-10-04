import os, sys, tempfile, unittest, json
from unittest.mock import patch
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import app
P={'role':'Sales Executive','experience':'1–3 years','language':'Tamil'}
class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); app.DB=self.tmp.name+'/test.db';app.DEMO=True;app.init()
        self.token=app.dispatch('POST','/auth/register',{'email':'a@example.com','password':'goodpassword123','profile':P})['token']
        self.user=app.user_for(self.token)['id']
    def tearDown(self):self.tmp.cleanup()
    def call(self,method,path,body={}):return app.dispatch(method,path,body,self.token)
    def start(self,key='request001'):return self.call('POST','/sessions',{'profile':P,'jd':'Maintain CRM and achieve sales targets','requestId':key})
    def test_full_interview_resume_and_history(self):
        s=self.start();self.assertEqual(len(s['questions']),5);self.assertIn('CRM',s['questions'][1]['text'])
        self.call('PUT',f'/sessions/{s["id"]}/draft',{'index':0,'text':'எனக்கு விற்பனை அனுபவம் உள்ளது'})
        self.assertIn('எனக்கு',self.call('GET',f'/sessions/{s["id"]}')['drafts']['0'])
        for i in range(5):s=self.call('POST',f'/sessions/{s["id"]}/answer',{'index':i,'text':'I listened to the customer, explained the options and arranged a follow-up call.'})
        self.assertTrue(all(len(a)==1 for a in s['answers']))
        self.assertEqual(s['answers'][0][0]['feedback']['stronger'],s['answers'][0][0]['text'])
        self.assertEqual(len(self.call('GET','/sessions')),1)
    def test_idempotent_create_and_answer(self):
        s=self.start();self.assertEqual(self.start()['id'],s['id']);self.assertEqual(app.allowance(self.user)['used'],1)
        body={'index':0,'text':'I have experience in sales.'}
        self.call('POST',f'/sessions/{s["id"]}/answer',body)
        self.assertEqual(len(self.call('POST',f'/sessions/{s["id"]}/answer',body)['answers'][0]),1)
    def test_delete_does_not_reset_free_allowance(self):
        s=self.start();self.call('DELETE',f'/sessions/{s["id"]}')
        with self.assertRaises(app.APIError) as e:self.start('request002')
        self.assertEqual(e.exception.status,402)
    def test_generation_failure_refunds(self):
        with patch.object(app,'questions',side_effect=app.APIError('offline',503)):
            with self.assertRaises(app.APIError):self.start()
        self.assertEqual(app.allowance(self.user)['used'],0)
        self.start()
    def test_cross_account_access_is_denied(self):
        s=self.start();other=app.dispatch('POST','/auth/register',{'email':'b@example.com','password':'goodpassword123','profile':P})['token']
        for method in ['GET','DELETE']:
            with self.assertRaises(app.APIError) as e:app.dispatch(method,f'/sessions/{s["id"]}',{},other)
            self.assertEqual(e.exception.status,404)
    def test_retry_budget(self):
        s=self.start()
        for i in range(3):self.call('POST',f'/sessions/{s["id"]}/answer',{'index':0,'text':f'Attempt {i}: I supported the customer.'})
        with self.assertRaises(app.APIError):self.call('POST',f'/sessions/{s["id"]}/answer',{'index':0,'text':'A fourth attempt.'})
    def test_account_delete_cascades(self):
        self.start();self.call('DELETE','/me')
        with self.assertRaises(app.APIError):app.user_for(self.token)
        with app.db() as c:
            for table in ['users','tokens','sessions','usage']:self.assertEqual(c.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
    def test_expired_and_forged_payments(self):
        self.start()
        with self.assertRaises(app.APIError):self.call('POST','/billing/sync',{'plan':'month','paid':True})
        self.assertEqual(app.allowance(self.user)['plan'],'free')
    def test_verified_subscription_renewal_resets_bucket(self):
        data={'subscriber':{'subscriptions':{'interviewready_monthly':{'purchase_date':'2026-01-01T00:00:00Z','expires_date':'2099-01-01T00:00:00Z'}},'non_subscriptions':{}}}
        with patch.dict(os.environ,{'REVENUECAT_SECRET_KEY':'test'}),patch.object(app,'remote',return_value=data):
            a=self.call('POST','/billing/sync');self.assertEqual(a['plan'],'month');self.start();self.assertEqual(app.allowance(self.user)['used'],1)
            data['subscriber']['subscriptions']['interviewready_monthly']['purchase_date']='2026-02-01T00:00:00Z'
            self.assertEqual(self.call('POST','/billing/sync')['used'],0)
    def test_live_feedback_validation_rejects_bad_shape(self):
        app.DEMO=False
        with patch.object(app,'ai',return_value={'scores':{'relevance':99}}):
            with self.assertRaises(app.APIError):app.feedback({'text':'Hi'},'test',P)
    def test_http_public_routes_accept_empty_or_stale_auth(self):
        import threading, urllib.request
        from http.server import ThreadingHTTPServer
        httpd=ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
        thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start()
        try:
            url=f'http://127.0.0.1:{httpd.server_port}'
            req=urllib.request.Request(url+'/config',headers={'Authorization':'Bearer'})
            with urllib.request.urlopen(req) as r:self.assertTrue(json.load(r)['demo'])
            data=json.dumps({'email':'http@example.com','password':'securepassword','profile':P}).encode()
            req=urllib.request.Request(url+'/auth/register',data=data,headers={'Authorization':'Bearer expired','Content-Type':'application/json'})
            with urllib.request.urlopen(req) as r:self.assertIn('token',json.load(r))
        finally:httpd.shutdown();httpd.server_close()
    def test_login_logout(self):
        tok=app.dispatch('POST','/auth/login',{'email':'a@example.com','password':'goodpassword123'})['token']
        app.dispatch('POST','/logout',{},tok)
        with self.assertRaises(app.APIError):app.user_for(tok)
if __name__=='__main__':unittest.main()
