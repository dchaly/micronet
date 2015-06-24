from django.http import HttpResponse
from django.shortcuts import render
from micronet.models import Node, Connection, NodeType


SCRIPT = """from mininet.topo import Topo
DATA=%(topology)s
METHODS=%(methods)s
ORDER=%(order)s
class GenerateTopo(Topo):
    def build(self):
        for type in ORDER:
            method = getattr(self, METHODS[type])
            for args, kwargs in DATA[type].items():
                method(*args, **kwargs)


def configure(net, items, node):
    for item in items:
        item.config(DATA[node][(item.name,)])
"""


def show(request):
    for c in Connection.objects.all():
        c.delete()
    for n in Node.objects.all():
        n.delete()
    return render(request, 'graph.html', {"test": "adsfds"})


def new_node(request):
    try:
        node = Node.objects.create(id_name=request.POST["id"],
                                   name=request.POST["name"].split()[0],
                                   type=NodeType.objects.get(name=request.POST["type"]))
        node.dpid = to_hex_str(node.id_node)
        node.save()
    except Exception as e:
        print(e)
    return HttpResponse("ok")


def new_connection(request):
    try:
        Connection.objects.create(id_name=request.POST["id"],
                                  label=request.POST["id"],
                                  node1=Node.objects.get(id_name=request.POST["node1"]),
                                  node2=Node.objects.get(id_name=request.POST["node2"]))
    except Exception as e:
        print(e)
        print(str(Node.objects.get(name=request.POST["target"])))
    return HttpResponse("ok")


def delete_node(request):
    try:
        node = Node.objects.get(id_name=request.POST["id"])
        sources = Connection.objects.filter(node1=node)
        targets = Connection.objects.filter(node2=node)
        for source in sources:
            source.delete()
        for target in targets:
            target.delete()
        node.delete()
    except Exception as e:
        print(e)
    return HttpResponse("ok")


def delete_connection(request):
    try:
        conn = Connection.objects.filter(id_name=(request.POST["id"]))
        for con in conn:
            con.delete()
    except Exception as e:
        print(e)
    return HttpResponse("ok")


def to_None(var):
    if var == "":
        return None
    return var


def set_connection_info(request):
    try:
        con = Connection.objects.get(id_name=request.POST["id"])
        con.label = request.POST["label"]
        con.loss = int(request.POST["loss"])
        con.max_queue_size = int(request.POST["queue"])
        con.save()
    except Exception as e:
        print(e)
        print(str(Node.objects.get(id_name=request.POST["target"])))
    return HttpResponse("ok")


def set_node_label(request):
    try:
        node = Node.objects.get(id_name=request.POST["id"])
        node.name = request.POST["label"]
        node.mac = to_None(request.POST["mac"])
        node.ip = to_None(request.POST["ip"])
        node.save()
        print(request)
    except Exception as e:
        print(e)
        print(str(Node.objects.get(name=request.POST["target"])))
    return HttpResponse("ok")


def to_hex_str(djt):
    return "".join(["0"]*(16-len(str(djt)))) + str(djt)


def _get_kat_topo():
    topo = ""
    nodes_port = {n: 1 for n in Node.objects.filter(type=NodeType.objects.get(name="switch"))}
    for con in Connection.objects.all():
        if con.node1.type.name == "switch" and con.node2.type.name == "switch":
            topo += "#(sw=" + con.node1.name + "*pt=" + str(nodes_port[con.node1]) \
                    + "*sw->" + con.node2.name + "*pt->" + str(nodes_port[con.node2]) + ")+" \
                    + "(sw=" + con.node2.name + "*pt=" + str(nodes_port[con.node2]) \
                    + "*sw->" + con.node1.name + "*pt->" + str(nodes_port[con.node1]) + ")+\n"
            nodes_port[con.node1] += 1
            nodes_port[con.node2] += 1
        if con.node1.type.name == "switch" and con.node2.type.name != "switch":
            topo += "#(sw=" + con.node1.name + "*pt" + str(nodes_port[con.node1]) + ")+\n"
            nodes_port[con.node1] += 1
        if con.node2.type.name == "switch" and con.node1.type.name != "switch":
            topo += "#(sw=" + con.node2.name + "*pt" + str(nodes_port[con.node2]) + ")+\n"
            nodes_port[con.node2] += 1
    return topo[0:-2]


def _get_script():
    result = {}
    for t in NodeType.objects.all():
        attrs = Node.get_attrs()
        result[str(t.name)] = {}
        for node in Node.objects.filter(type=t):
            name = tuple(str(getattr(node, at)) for at in attrs["key"])
            result[str(t.name)][name] = {}
            for attr in attrs["config"]:
                a = getattr(node, attr)
                if a:
                    result[str(t.name)][name][str(attr)] = str(a)
    result["link"] = {}
    for link in Connection.objects.all():
        con = tuple([str(link.node1), str(link.node2)])
        result["link"][con] = {}
    return SCRIPT % {"topology": str(result),
                       "methods": str({"host": "addHost", "switch": "addSwitch", "link": "addLink"}),
                       "order": str(["switch", "host", "link"])}


def get_script(request):
    try:
        result = _get_script()
        topo = _get_kat_topo()
        with open("C:/Users/dns/Desktop/Documents/vb_mininet/topo.py", "w") as f:
            f.write("# KAT topology\n")
            f.write(topo+"\n\n")
            f.write(result)

        return render(request, 'script.html',
                      {"topo": str(result),
                       "methods": str({"host": "addHost", "switch": "addSwitch", "link": "addLink"}),
                       "order": str(["switch", "host", "link"])})
    except Exception as e:
        print("Except " + str(e))
