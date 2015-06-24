from django.db import models


class NodeType(models.Model):
    id_type = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, null=False)
    def __str__(self):
        return ' '.join([
            self.name,
        ])
    @staticmethod
    def get_attrs():
        return {"key": ["id_type"], "config": ["name"]}


class Node(models.Model):
    id_node = models.AutoField(primary_key=True)
    id_name = models.CharField(max_length=200)
    name = models.CharField(max_length=45, null=False, unique=True)
    mac = models.CharField(max_length=24, null=True)
    ip = models.GenericIPAddressField(null=True, unique=True)
    dpid = models.CharField(max_length=16, null=True)
    type = models.ForeignKey(NodeType)
    def __str__(self):
        return ' '.join([
            self.name,
        ])
    @staticmethod
    def get_attrs():
        return {"key": ["name"], "config": ["mac", "ip"]}


class Connection(models.Model):
    id_connection = models.AutoField(primary_key=True)
    id_name = models.CharField(max_length=45, null=False)
    label = models.CharField(max_length=200)
    node1 = models.ForeignKey(Node, related_name='target')
    node2 = models.ForeignKey(Node, related_name='source')
    bw = models.IntegerField(null=True)
    max_queue_size = models.IntegerField(null=True)
    loss = models.IntegerField(null=True)
    def __str__(self):
        return ' '.join([
            self.label,
        ])
    @staticmethod
    def get_attrs():
        return {"key": ["id_name"], "config": ["node1", "node2"]}


