# -*- coding: utf-8 -*-
"""
Created on Wed May 19 19:06:16 2021

@author: j23793276
"""
from functools import reduce
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
import random

class MJ18(ABEncMultiAuth):
    def __init__(self, groupObj, authNum, kVal, verbose=False):
        ABEncMultiAuth.__init__(self)
        global group, auth_num, k
        group = groupObj
        auth_num = authNum
        k = kVal
    
    def setup(self):
        g1 = group.random(G1)
        g2 = group.random(G2)
        g1.initPP()
        g2.initPP()
        g1_A = []#(k+1)*k
        A = []#(k+1)*k
        U = []#(k+1)*(k+1)
        for i in range(k+1):
            tmp1 = []
            tmp2 = []
            for j in range(k):
                a = group.random(ZR)
                val = g1 ** a
                tmp1.append(val)
                tmp2.append(a)
            g1_A.append(tmp1)
            A.append(tmp2)
        
        for i in range(k+1):
            tmp = []
            for j in range(k+1):
                tmp.append(group.random(ZR))
            U.append(tmp)
        
        #print("U:",U)
        UT = [list(i) for i in zip(*U)]#(k+1)*(k+1)
        #print("UT:",UT)
        UTA = []#(k+1)*k
        UTA = matrixMul(UT, A)
        g1_UTA = []#(k+1)*k
        for i in range(k+1):
            tmp = []
            tmp = list(map(lambda x: g1 ** x,UTA[i]))
            g1_UTA.append(tmp)
        #print(len(g1_UTA))
        #print(len(g1_UTA[0]))
            
        pp = {'g1':g1, 'g2':g2, 'g1_A':g1_A, 'g1_UTA':g1_UTA} 
        
        return pp
       
    def authsetup(self, pp, number):
        W_i = []#(k+1)*(k+1)
        for i in range(k+1):
            tmp = []
            for j in range(k+1):
                tmp.append(group.random(ZR))
            W_i.append(tmp)
        
        alpha_i = []#(k+1)*1
        for i in range(k+1):
            tmp = []
            tmp.append(group.random(ZR))
            alpha_i.append(tmp)
            
        alpha_iT = [list(i) for i in zip(*alpha_i)]#1*(k+1)
        
        sigma_i = group.random(ZR)#1
        #print("\nalpha_iT :=>",alpha_iT)
        
        MSK_i = {'W_i':W_i, 'alpha_i':alpha_i, 'sigma_i':sigma_i}
        
        W_iT = [list(i) for i in zip(*W_i)]   #(k+1)*(k+1)
        g1_AT = [list(i) for i in zip(*pp['g1_A'])] #k*(k+1)
        
        g1_WiTA = []
        for i in range(k):
            tmp = []
            for j in range(k+1):
                mapping1 = map(lambda x,y: x**y,g1_AT[i],W_iT[j])
                summarize = reduce(lambda x,y:x*y, list(mapping1))
                tmp.append(summarize)
            g1_WiTA.append(tmp)
        g1_WiTA = [list(i) for i in zip(*g1_WiTA)] 
        #print("\ng1_WiTA :=>",g1_WiTA)
        
        g2_alphaiT = []#1*(k+1)
        for i in range(1):
            tmp = []
            for j in range(k+1):
                tmp.append(pp['g2'] ** alpha_iT[0][j])
            g2_alphaiT.append(tmp)
         
        e_g1_g2_alphaiTA = []#1*k
        for i in range(k):
            prod = 1
            tmp = []
            for j in range(k+1):
                prod = prod * pair(g2_alphaiT[0][j],g1_AT[i][j])
            tmp.append(prod)
            e_g1_g2_alphaiTA.append(tmp)
        e_g1_g2_alphaiTA = [list(i) for i in zip(*e_g1_g2_alphaiTA)]   
        #print("123:",e_g1_g2_alphaiTA)  
        #print(len(e_g1_g2_alphaiTA))
        #print(len(e_g1_g2_alphaiTA[0]))
        y_i = pp['g2'] ** sigma_i
        
        PK_i = {'g1_WiTA':g1_WiTA, 'e_g1_g2_alphaiTA':e_g1_g2_alphaiTA, 'y_i':y_i}        
        
        return PK_i, MSK_i
        
    def encrypt(self, pp, allPK, M, X):
        s = []#k*1
        for i in range(k):
            tmp = []
            tmp.append(group.random(ZR))
            s.append(tmp)
        s_T = [list(i) for i in zip(*s)]#1*k
        
        g1_As = []#(k+1)*1
        for i in range(k+1):
            tmp = []
            mapping3 = map(lambda x,y: x**y,pp['g1_A'][i],s_T[0])
            summarize = reduce(lambda x,y:x*y, list(mapping3))
            tmp.append(summarize)
            g1_As.append(tmp)
        #print(g1_As)
        
        C_i = []
        xis_T = []
        #allxis_T = []
        allC_i = []
        for n in range(auth_num):
            for i in range(1):
                tmp = []
                for j in range(k):
                     tmp.append(s_T[i][j] * X[n])
                xis_T.append(tmp)
            #allxis_T.append(xis_T)
        #print(len(xis_T))
        #print(len(xis_T[0])) 
        
        #print(xis_T) 
                
        for n in range(auth_num):
            C_i = []
            for i in range(k+1):
                tmp = []
                for j in range(1):
                    mapping4 = map(lambda x,y: x ** y,pp['g1_UTA'][i],xis_T[n])
                    summarize1 = reduce(lambda x,y:x*y, list(mapping4))
                    
                    mapping5 = map(lambda x,y: x ** y,allPK[n]['g1_WiTA'][i],s_T[j])
                    summarize2 = reduce(lambda x,y:x*y, list(mapping5))
                    tmp.append(summarize1 * summarize2)
                C_i.append(tmp)
            allC_i.append(C_i)
        
        #print(len(allC_i))
        #print(len(allC_i[0]))
        #print(C_i)
                    
        
        prod_e_g1_g2_alphaiTA = []#1*k
        for i in range(k):
            prod = 1
            tmp = []
            for j in range(auth_num):
                prod = prod * allPK[j]['e_g1_g2_alphaiTA'][0][i]
            tmp.append(prod)
            prod_e_g1_g2_alphaiTA.append(tmp)
            
        prod_e_g1_g2_alphaiTA = [list(i) for i in zip(*prod_e_g1_g2_alphaiTA)]
        #print(len(prod_e_g1_g2_alphaiTA))
        #print(len(prod_e_g1_g2_alphaiTA[0]))
        for i in range(1):
            for j in range(1):
                mapping6 = map(lambda x,y: x**y,prod_e_g1_g2_alphaiTA[i],s_T[j])
                summarize = reduce(lambda x,y:x*y, list(mapping6))
        C_p = M * summarize
        #print(C_p)
        ct = {'C_0':g1_As, 'C_i':allC_i, 'C_p':C_p}
        
        return ct
    
    def keygen(self, pp, allPK, MSK_i, GID, V, number):
        #print("\n")
        tmp = []
        tmp1 = []
        tmp2 = []       
        mu_i = []
         
        
        leftRes = []
        for i in range(k+1): 
            tmp = []
            tmp.append(0)
            leftRes.append(tmp)        
        
        for i in range(number):
            tmp = []
            tmp1 = []
            val = allPK[i]['y_i'] ** MSK_i['sigma_i']
            hashInput = [val, GID, V]
            hashVal = group.hash(hashInput, ZR)
            tmp.append(hashVal)
            for j in range(k+1):
                tmp1.append(tmp)
            for m in range(k+1):
                leftRes[m][0] = leftRes[m][0] + tmp1[m][0]
            
            
        rightRes = []
        for i in range(k+1): 
            tmp = []
            tmp.append(0)
            rightRes.append(tmp)
            
        for i in range(auth_num-number-1):
            tmp = []
            tmp2 = []
            val = allPK[i+number+1]['y_i'] ** MSK_i['sigma_i']
            hashInput = [val, GID, V]
            hashVal = group.hash(hashInput, ZR)
            tmp.append(hashVal)
            for j in range(k+1):
                tmp2.append(tmp)
            for m in range(k+1):
                rightRes[m][0] = rightRes[m][0] + tmp2[m][0]
            #print("number:",number)
            #print(i+number+1)
            #print(len(rightRes))
            #print(len(rightRes[0]))
        for i in range(k+1):
            mu_i.append(leftRes[i][0] - rightRes[i][0]) 
        
        
        g2_h = []        
        for i in range(k+1):
            tmp = []
            #hashInput2 = [GID, V]
            hashVal2 = group.hash(GID, G2)
            tmp.append(hashVal2)
            g2_h.append(tmp)
        #print(len(mu_i))
        #print(len(mu_i[0]))
        g2_hT = [list(i) for i in zip(*g2_h)]
        
        g2_mu_i = []#(k+1)*1
        for i in range(k+1):
            tmp = []
            tmp.append(pp['g2'] ** mu_i[i])
            g2_mu_i.append(tmp)
        #print(len(g2_mu_i))
        #print(len(g2_mu_i[0]))   
        g2_alpha_i = []
        for i in range(k+1):  
            tmp = []
            tmp.append(pp['g2'] ** MSK_i['alpha_i'][i][0])
            g2_alpha_i.append(tmp)
        #print(len(g2_alpha_i))
        #print(len(g2_alpha_i[0]))      
        v_iW_i = []
        for i in range(k+1):
            tmp = []
            for j in range(k+1):
                tmp.append(MSK_i['W_i'][i][j] * V[number] * (-1))
            v_iW_i.append(tmp)
        #print(len(v_iW_i))
        #print(len(v_iW_i[0])) 
        g2_v_iW_ih = []
        for i in range(1):
            tmp = []
            for j in range(k+1):
                mapping7 = map(lambda x,y: x ** y, g2_hT[i], v_iW_i[j])
                summarize = reduce(lambda x,y:x*y, list(mapping7))
                tmp.append(summarize)
            g2_v_iW_ih.append(tmp)
        g2_v_iW_ih = [list(i) for i in zip(*g2_v_iW_ih)]
        #print(len(g2_v_iW_ih))
        #print(len(g2_v_iW_ih[0]))
        
        K_i = []
        for i in range(k+1):
            tmp = []
            for j in range(1):
                tmp.append(g2_alpha_i[i][j] * g2_v_iW_ih[i][j] * g2_mu_i[i][j])
            K_i.append(tmp)
        #print(len(K_i))
        #print(len(K_i[0]))
        #print(len(g2_h[0]))
        #print(type(mu_i[0][0]))
        sk_i = {'H(GID,V)':g2_h, 'K_i':K_i}
        return sk_i
       
    def decrypt(self, allsk, ct, V):
        
        prodOfK_i = []
        prodOfC_iv_i = []
        for i in range(k+1):
            prodOfK_i.append([])
            prodOfC_iv_i.append([])
            for j in range(1):
                prodOfK_i[i].append(1)
                prodOfC_iv_i[i].append(1)
                
        for n in range(auth_num):
            for i in range(k+1):
                for j in range(1):
                    prodOfK_i[i][0] = prodOfK_i[i][0] * allsk[n]['K_i'][i][0]
                    prodOfC_iv_i[i][0] = prodOfC_iv_i[i][0] * (ct['C_i'][n][i][0] ** V[n])
        
        prod1 = 1 
        prod2 = 1
        for i in range(k+1):
            for j in range(1):
                prod1 = prod1 * pair(ct['C_0'][i][0], prodOfK_i[i][0])
                prod2 = prod2 * pair(allsk[0]['H(GID,V)'][i][0], prodOfC_iv_i[i][0])
                #print(prod2)
        prod = prod1 * prod2
        return ct['C_p'] / prod

def dot(V1,V2):
    innerProd = 0
    if len(V1) != len(V2):
        return -1
    else:
        for i in range(len(V1)):
            innerProd = innerProd + V1[i]*V2[i]    
    return innerProd
    
def matrixMul(L1, L2): 
    res = []
    L2T = [list(i) for i in zip(*L2)]
    for i in range(len(L1)):#3
        tmp = []
        for j in range(len(L2[0])):#2
            mapping = map(lambda x,y: x*y, L1[i],L2T[j])
            summarize = reduce(lambda x,y:x+y, list(mapping))
            tmp.append(summarize)
        res.append(tmp)
    return res
       
def main():
    groupObj = PairingGroup('SS512')
    authNum = 4
    kVal = 3
    dipe = MJ18(groupObj, authNum, kVal)
    pp = dipe.setup()
    #print("\npp :=>", pp)
    allPK = []
    allMSK = []
    for i in range(authNum):
        PK_i, MSK_i = dipe.authsetup(pp,i)
        allPK.append(PK_i)
        allMSK.append(MSK_i)
    
    X = []
    for i in range(authNum):
        X.append(group.random(ZR))
    #print("\nX =>", X)
    
    M = groupObj.random(GT)
    print("\nM =>", M)
    ct = dipe.encrypt(pp, allPK, M, X)
    
    sum = 0
    V = []
    for i in range(len(X)-1):
        tmp = group.random(ZR)
        sum = sum + X[i] * tmp
        V.append(tmp)
    V.append(-sum/X[len(X)-1])
    #print("\nV =>", V)
    #print(dot(X,V))
    gidLen = 10
    GID = ""
    for i in range(gidLen):
        GID = GID + str(random.randint(0,1))    
    
    allsk = []
    #mu = [[0],[0],[0]]
    for i in range(authNum):
        sk_i = dipe.keygen(pp, allPK, allMSK[i], GID, V, i)
        
        #for j in range(kVal+1):        
            #mu[j][0] = mu[j][0] + sk_i['mu_i'][j]
        
        allsk.append(sk_i)
    #print("\nmu:",mu)
        
    rec_M = dipe.decrypt(allsk, ct, V)
    print("\nRec_M =>", rec_M)
    
if __name__ == "__main__":
    main()