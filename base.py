import pymysql
from apscheduler.schedulers.background import BackgroundScheduler
from loger import HandleLog
# 连接数据库
import time
from threading import Lock
log = HandleLog()
lock = Lock()
class loader_db:
    def __init__(self, host='43.143.44.146',port=3306, user=None, passwd=None, db_name = None) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db_name = db_name
        self.last_op_time = time.time()
    
    def connect(self):
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd,charset='utf8',connect_timeout=2,cursorclass=pymysql.cursors.DictCursor,autocommit=True,database='loader_temp')
            self.cursor = self.conn.cursor()
            self.loop()
        except Exception as e:
            log.error(e)
            return False
        return True

    def update_material(self):
        r = self.query("SELECT * FROM {};".format("material"))
        ret = {}
        for i,n in enumerate(r):
            ret.update({i:n['name']})
        return ret

    def _keep_alive(self):
        if time.time() - self.last_op_time > 10:
            lock.acquire()
            self.conn.ping(reconnect=True)
            lock.release()
            log.debug('_keep_alive')

    def loop(self):
        self.sched = BackgroundScheduler()
        self.sched.add_job(self._keep_alive, 'interval', seconds=10)
        self.sched.start()
    
    def query(self, sql):
        self.last_op_time = time.time()
        lock.acquire()
        self.cursor.execute(sql)
        lock.release()
        return self.cursor.fetchall()

    def cleanup(self):
        self.conn.close()
        log.debug('sql connection close')
        self.sched.shutdown()
        log.debug('scheduler shutdown')

    def update_data(self, db_name):
        lock.acquire()
        self.cursor.execute("SELECT * FROM {};".format(db_name))
        ret = self.cursor.fetchall()
        lock.release()
        return ret
