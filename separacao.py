from gurobipy import *
from atalhos import pertence
from atalhos import cruzam

def listaDe(k, l, tuplas):
	for par in tuplas[k]:
		if l == par[0]:
			return par[1]
	return None


def separacao(model, where):
	
	if where == GRB.Callback.MIPNODE:
		if model.cbGet(GRB.Callback.MIPNODE_STATUS) == GRB.Status.OPTIMAL:
			print("======================================================")
			
			x = model.cbGetNodeRel(model._vars)
			for i in model._coloridos:
				for cand in model._tuplas[i]:
					j = cand[0]
					for par in itertools.product(cand[1],cand[1]):
						k = par[0]
						l = par[1]
						if k < l and x[i] + x[j] + x[k] + x[l] < 1.95:				
							lista = listaDe(k,l,model._tuplas)
							if lista != None:
								if i in lista and j in lista:
									model.cbCut(model._vars[i] + model._vars[j] + model._vars[k] + model._vars[l] >= 2)
									print(model._vars[i] + model._vars[j] + model._vars[k] + model._vars[l] >= 2)
									print("{} {} {} {}".format(x[i], x[j], x[k], x[l]))
									return
			
	elif where == GRB.Callback.MIPSOL:	
		print("#######################################################")
		sol = model.cbGetSolution(model._vars)
		aSol = [i for i in model._azuis if sol[i] < 0.9]
		if not aSol:
			return 
		vSol = [i for i in model._verms if sol[i] < 0.9]
		if not vSol:
			return 
		print(model.cbGet(GRB.Callback.MIPSOL_OBJ))
		
		fazParteASol, verticeASol = pertence(model._g, vSol[:], aSol[:])

		if fazParteASol:
			model.cbLazy(quicksum([model._vars[i] for i in vSol + [verticeASol]]) >= 1)

		fazParteVSol, verticeVSol = pertence(model._g, aSol[:], vSol[:])

		if fazParteVSol:
			model.cbLazy(quicksum([model._vars[i] for i in aSol + [verticeVSol]]) >= 1)

		if cruzam(model._g, aSol[:], vSol[:], model._brancos):
			#print(quicksum([model._vars[i] for i in aSol + vSol]) >= 1)
			model.cbLazy(quicksum([model._vars[i] for i in aSol + vSol]) >= 1)