import psycopg2

def rg_prediction(name,conn,cur,first):
    if(first):
        cur.execute("update rotogrinders_predictions set linked = %s",(False,))
        conn.commit()
        print("reset")
        
    cur.execute("select predicted from rotogrinders_predictions where nba_name = %s",(name,))
    if(cur.rowcount == 0):
        return None
    else:
        val =  cur.fetchall()[0][0]
        cur.execute("update rotogrinders_predictions set linked = %s where nba_name = %s",(True,name))
        conn.commit()
        return val

def getHeuristic(name,strat,conn,cur,first):
    if (strat == "rg"):
        return rg_prediction(name,conn,cur,first)
