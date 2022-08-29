import operator

from django.http import HttpResponse
from django.shortcuts import render, redirect
from rdkit import Chem,DataStructs
import rdkit
from rdkit.Chem import AllChem,Descriptors,Draw
from .models import mol_props
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage

# Create your views here.
def registration(request):
    if request.method == 'POST':
        if request.POST.get('getsmiles') != '':
            #分子属性及ID
            smiles = request.POST.get('getsmiles')
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                tpsa = round(Descriptors.TPSA(mol),3)
                logp = round(Descriptors.MolLogP(mol),3)
                mw = round(Descriptors.MolWt(mol),3)
                if mol_props.objects.all().count() != 0:
                    compound_id_last = mol_props.objects.order_by('-compound_id').first().compound_id
                    #print(compound_id_last)
                    id = compound_id_last.split('-')[1]
                    id_1 = int(id)+1
                    id_2 = str(id_1).zfill(6)
                    compound_id = 'QL-' + id_2
                    # 分子图片输出
                    Draw.MolToFile(mol, './register/template/static/mol_image/%s.png' % compound_id)
                    img_path = '/static/mol_image/%s.png' % compound_id
                else:
                    compound_id = 'QL-000001'
                    # 分子图片输出
                    Draw.MolToFile(mol, './register/template/static/mol_image/%s.png' % compound_id)
                    img_path = '/static/mol_image/%s.png' % compound_id
                #分子图片输出
                Draw.MolToFile(mol, './register/template/static/mol_image/%s.png' % compound_id)
                img_path = '/static/mol_image/%s.png' % compound_id
                #render进html页面
                ctx = {}
                ctx['tpsa'] = tpsa
                ctx['logp'] = logp
                ctx['mw'] = mw
                ctx['compound_id'] = compound_id
                ctx['img_path'] = img_path
                ctx['smiles'] = smiles
                return render(request,'registration.html',locals())
            else:
                return HttpResponse('化合物结构错误，请重新输入！')
        else:
            return redirect("/index/")




def reg_result(request):
    if request.method == 'POST':
        smiles_original = request.POST.get('smiles')
        logp = request.POST.get('logp')
        mw = request.POST.get('mw')
        compound_id = request.POST.get('compound_id')
        img_path = request.POST.get('img_path')
        tpsa = request.POST.get('tpsa')
        #convert to canonsmiles
        smiles = rdkit.Chem.CanonSmiles(smiles_original, useChiral=1)
        mol_mem = Chem.MolFromSmiles(smiles)
        mol = Chem.MolToMolBlock(mol_mem)
        mol_file_tmp = open('./register/template/static/mol_file/%s.mol' % compound_id,'w')
        mol_file_tmp.write(mol)
        mol_file_tmp.close()
        mol_file_path = '/static/mol_file/%s.mol' % compound_id
        #print(mol)
        fp = AllChem.GetMorganFingerprintAsBitVect(mol_mem, radius=2).ToBitString()
        #print(fp)
        if mol_props.objects.filter(smiles=smiles).exists():
            return HttpResponse('化合物已存在，请勿重复注册！')
        else:
            molecule_insert = mol_props.objects.create(compound_id=compound_id, smiles=smiles, mol_file=mol, TPSA=tpsa, xlogp=logp, MW=mw, img_file=img_path,fingerprint=fp, mol_file_path=mol_file_path)
            molecule_insert.save()
            return HttpResponse('化合物注册成功！')

def compoundlist(request):
    if request.session.get('is_login'):
        mol_list = mol_props.objects.all().order_by('-compound_id')
        paginator = Paginator(mol_list, 10)
        page = request.GET.get('page',1)
        print(page)
        try:
            sublist = paginator.page(page)
        except PageNotAnInteger:
            sublist = paginator.page(1)
        except EmptyPage:
            sublist = paginator.page(paginator.num_pages)
        return render(request, "compoundlist.html", {"sublist": sublist})
    else:
        return redirect("/login/")

def search(request):
    if request.session.get('is_login'):
        ##相似性结构检索，输入Similarity数值以及不输入Similarity数值
        if request.POST.get('getsearchsmiles') != '' and request.POST.get('property_name') =='Similarity' and request.POST.get('property_value') !='':
            getsearchsmiles = request.POST.get('getsearchsmiles')
            getsimilarity = float(request.POST.get('property_value'))
            getsearchmol = Chem.MolFromSmiles(getsearchsmiles)
            getsearchmol_fp = Chem.AllChem.GetMorganFingerprint(getsearchmol,2)
            if getsearchmol:
                mol_list = mol_props.objects.all()
                search_result = []
                for item in mol_list:
                    search_dict = {}
                    smiles = item.smiles
                    mol = Chem.MolFromSmiles(smiles)
                    fp = Chem.AllChem.GetMorganFingerprint(mol,2)
                    similarity =DataStructs.DiceSimilarity(fp,getsearchmol_fp)
                    if similarity > getsimilarity:
                        search_dict['compound_id'] = item.compound_id
                        search_dict['img_file'] = item.img_file
                        search_dict['smiles'] = item.smiles
                        search_dict['mol_file_path'] = item.mol_file_path
                        search_dict['MW'] = item.MW
                        search_dict['similarity'] = round(similarity,3)
                        search_result.append(search_dict)
                search_result_sorted = sorted(search_result,key=operator.itemgetter('similarity'),reverse=True)
                return render(request,'search.html',{'search_result_sorted':search_result_sorted})
        if request.POST.get('getsearchsmiles') != '' and request.POST.get('property_name') =='Similarity' and request.POST.get('property_value') =='':
            return HttpResponse('请输入相似性数值！')

        ##属性检索Compound ID
        if request.POST.get('property_name') =='Compound ID':
            property_value = request.POST.get('property_value')
            mol_list = mol_props.objects.all()
            search_result = []
            for mol in mol_list:
                search_dict = {}
                if property_value.upper() in mol.compound_id.upper():
                    search_dict['compound_id'] = mol.compound_id
                    search_dict['img_file'] = mol.img_file
                    search_dict['smiles'] = mol.smiles
                    search_dict['MW'] = mol.MW
                    search_dict['mol_file_path'] = mol.mol_file_path
                    search_dict['similarity'] = 1
                    search_result.append(search_dict)
                #else:
                 #   return HttpResponse('没有检索到包含此ID的化合物！')
            if len(search_result)==0:
                return HttpResponse('没有检索到包含此ID的化合物！')
            else:
                search_result_sorted = sorted(search_result, key=operator.itemgetter('compound_id'), reverse=False)
            return render(request, 'search.html', {'search_result_sorted': search_result_sorted})

        ##属性检索MW
        if request.POST.get('property_name') =='MW':
            property_value = float(request.POST.get('property_value'))
            qf = request.POST.get('property_qualifier')
            #print(qf)
            mol_list = mol_props.objects.all()
            search_result = []
            if qf == '<':
                for mol in mol_list:
                    search_dict = {}
                    if mol.MW < property_value:
                        search_dict['compound_id'] = mol.compound_id
                        search_dict['img_file'] = mol.img_file
                        search_dict['smiles'] = mol.smiles
                        search_dict['MW'] = mol.MW
                        search_dict['mol_file_path'] = mol.mol_file_path
                        search_dict['similarity'] = 1
                        search_result.append(search_dict)
            if qf == '>':
                for mol in mol_list:
                    search_dict = {}
                    if mol.MW > property_value:
                        search_dict['compound_id'] = mol.compound_id
                        search_dict['img_file'] = mol.img_file
                        search_dict['smiles'] = mol.smiles
                        search_dict['MW'] = mol.MW
                        search_dict['mol_file_path'] = mol.mol_file_path
                        search_dict['similarity'] = 1
                        search_result.append(search_dict)
            if qf == '=':
                for mol in mol_list:
                    search_dict = {}
                    if mol.MW == property_value:
                        search_dict['compound_id'] = mol.compound_id
                        search_dict['img_file'] = mol.img_file
                        search_dict['smiles'] = mol.smiles
                        search_dict['MW'] = mol.MW
                        search_dict['mol_file_path'] = mol.mol_file_path
                        search_dict['similarity'] = 1
                        search_result.append(search_dict)
                #else:
                 #   return HttpResponse('没有检索到包含此ID的化合物！')
            if len(search_result)==0:
                return HttpResponse('没有检索到包此MW范围的化合物！')
            else:
                search_result_sorted = sorted(search_result, key=operator.itemgetter('MW'), reverse=False)
            return render(request, 'search.html', {'search_result_sorted': search_result_sorted})
        else:
            return redirect('/index/')
    else:
        return redirect("/login/")


