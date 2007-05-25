# -*- python -*-
# -*- coding: latin-1 -*-
#
#       PortGraph : graph package
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#                       Fred Theveny <frederic.theveny@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       VPlants WebSite : https://gforge.inria.fr/projects/vplants/


__doc__="""
This module provide an implementation of a dataflow
"""

__license__= "Cecill-C"
__revision__=" $Id: graph.py 116 2007-02-07 17:44:59Z tyvokka $ "

from openalea.graph.property_graph import PropertyGraph,InvalidVertex,InvalidEdge
from openalea.graph.id_generator import IdGenerator


class PortError (Exception) :
	pass


class Port (object) :
	"""
	simple structure to maintain some port property
	a port is an entry point to a vertex
	"""
	def __init__ (self, vid, local_pid, is_out_port) :
		#internal data to acces from dataflow
		self._vid = vid
		self._local_pid = local_pid
		self._is_out_port = is_out_port
		#external data
		self._capacity = -1
		self.description = "port"
		self._interface = None

	
	def capacity (self) :
		"""
		maximum number of edges that can
		be connected on this port
		-1 mean an infinity of connections
		:rtype: int
		"""
		return self._capacity

	
	def set_capacity (self, max_connections_nb) :
		"""
		set the maximum number of edges
		that can be connected to port pid
		set capacity to -1 to allow an infinity
		of connections
		"""
		self._capacity = max_connections_nb
	
	def interface (self) :
		return self._interface
	

	def set_interface (self, data_type) :
		self._interface = data_type
		

class DataFlow (PropertyGraph):
	"""
	Directed graph with connections between in_ports
	of vertices and out_port of vertices
	ports are typed
	"""

	def __init__ (self) :
		PropertyGraph.__init__(self)
		self._ports = {}
		self._pid_generator = IdGenerator()
		self.add_vertex_property("_ports")
		self.add_edge_property("_source_port")
		self.add_edge_property("_target_port")
		self.add_vertex_property("_actor")
		
	####################################################
	#
	#		edge port view
	#
	####################################################
	def source_port (self, eid) :
		"""
		out port of the source vertex
		of the edge
		:rtype: pid
		"""
		return self.edge_property("_source_port")[eid]
	

	def target_port (self, eid) :
		"""
		in port of the target vertex
		of the edge
		:rtype: pid
		"""
		return self.edge_property("_target_port")[eid]
	

	####################################################
	#
	#		vertex port view
	#
	####################################################

	def out_ports (self, vid=None) :
		"""
		iter on all out ports of a given vertex
		iter on all out ports of the dataflow
		if vid is None
		:rtype: iter of pid
		"""
		for pid in self.ports(vid) :
			if self.is_out_port(pid) :
				yield pid
	

	def in_ports (self, vid=None) :
		"""
		iter on all in ports of a given vertex
		iter on all in ports of the dataflow
		if vid is None
		:rtype: iter of pid
		"""
		for pid in self.ports(vid) :
			if self.is_in_port(pid) :
				yield pid
	
	def ports (self, vid=None) :
		"""
		iter on all ports of a given vertex
		iter on all ports of the dataflow
		if vid is None
		:rtype: iter of pid
		"""
		if vid is None :
			return iter(self._ports)
		else :
			return iter(self.vertex_property("_ports")[vid])


	####################################################
	#
	#		port view
	#
	####################################################

	def is_in_port (self, pid) :
		"""
		test whether port refered by pid
		is an in port of its vertex
		:rtype: bool
		"""
		return not self._ports[pid]._is_out_port
	

	def is_out_port (self, pid) :
		"""
		test whether port refered by pid
		is an out port of its vertex
		:rtype: bool
		"""
		return self._ports[pid]._is_out_port
	

	def vertex (self, pid) :
		"""
		return the id of the vertex which own the port
		:rtype: vid
		"""
		return self._ports[pid]._vid
	

	def connected_ports (self, pid) :
		"""
		iterate on all ports connected
		to this port
		:rtype: iter of pid
		"""
		if self.is_out_port(pid) :
			for eid in self.connected_edges(pid) :
				yield self.target_port(eid)
		else :
			for eid in self.connected_edges(pid) :
				yield self.source_port(eid)
	

	def connected_edges (self, pid) :
		"""
		iterate on all edges connected
		to this port
		:rtype: iter of eid
		"""
		vid=self.vertex(pid)
		if self.is_out_port(pid) :
			for eid in self.out_edges(vid) :
				if self.source_port(eid)==pid :
					yield eid
		else :
			for eid in self.in_edges(vid) :
				if self.target_port(eid)==pid :
					yield eid

	####################################################
	#
	#		local port concept
	#
	####################################################

	def port (self, pid) :
		"""
		port object specified by its global pid
		"""
		try :
			return self._ports[pid]
		except KeyError :
			raise PortError("port %s don't exist" % str(pid))

	
	def local_id (self, pid) :
		"""
		local port identifier of a given port
		specified by its global pid
		"""
		try :
			return self._ports[pid]._local_pid
		except KeyError :
			raise PortError("port %s don't exist" % str(pid))
		
	
	def out_port (self, vid, local_pid) :
		"""
		global port id of a given port
		:rtype: pid
		"""
		for pid in self.out_ports(vid) :
			if self._ports[pid]._local_pid == local_pid :
				return pid
		raise PortError ("Local pid '%s' does not exist" % str(local_pid))
	
	
	def in_port (self, vid, local_pid) :
		"""
		global port id of a given port
		:rtype: pid
		"""
		for pid in self.in_ports(vid) :
			if self._ports[pid]._local_pid == local_pid :
				return pid
		raise PortError ("local pid '%s' does not exist" % str(local_pid))
	
	#####################################################
	#
	#		associated actor
	#
	#####################################################
	def set_actor (self, vid, actor) :
		"""
		associate an actor to a given vertex
		"""
		self.vertex_property("_actor")[vid] = actor
		
	
	def actor (self, vid) :
		"""
		return actor associated to a given vertex
		"""
		return self.vertex_property("_actor")[vid]
	
	def add_actor (self, actor, vid=None) :
		"""
		create a vertex and the corresponding ports
		and associate it with the given actor
		return: vid
		"""
		vid=self.add_vertex(vid)
		for key,interface in actor.inputs() :
			self.add_in_port(vid,key)
			
		for key,interface in actor.outputs() :
			self.add_out_port(vid,key)
			
		self.set_actor(vid,actor)
		return vid
	
	#####################################################
	#
	#		mutable concept
	#
	#####################################################
	def add_in_port (self, vid, local_pid, pid=None) :
		"""
		add a new in port to vertex pid using local_pid
		use pid as global port id if specified or
		create a new one if None
		raise an error if pid is already used
		return pid used
		:rtyp: pid
		"""
		pid = self._pid_generator.get_id(pid)
		self._ports[pid] = Port(vid,local_pid,False)
		self.vertex_property("_ports")[vid].add(pid)
		return pid
	

	def add_out_port (self, vid, local_pid, pid=None) :
		"""
		add a new out port to vertex pid using local_pid
		use pid as global port id if specified or
		create a new one if None
		raise an error if pid is already used
		return pid used
		:rtyp: pid
		"""
		pid=self._pid_generator.get_id(pid)
		self._ports[pid] = Port(vid,local_pid,True)
		self.vertex_property("_ports")[vid].add(pid)
		return pid

	
	def remove_port (self, pid) :
		"""
		remove the specified port
		and all connections to this port
		"""
		for eid in list(self.connected_edges(pid)) :
			self.disconnect(eid)
		self.vertex_property("_ports")[self.vertex(pid)].remove(pid)
		self._pid_generator.release_id(pid)
		del self._ports[pid]
	

	def connect (self, source_pid, target_pid, eid=None) :
		"""
		connect the out port source_pid with
		the in_port target_pid
		use eid if not None or create a new one
		raise an error if eid is already used
		return eid used
		:rtype: eid
		"""
		if not self.is_out_port(source_pid) :
			raise PortError("source_pid %s is not an output port" % str(source_pid))
		if not self.is_in_port(target_pid) :
			raise PortError("target_pid %s is not an input port" % str(target_pid))

		for pid in (source_pid,target_pid) :
			if((self.port(pid).capacity() != -1) and 
			   (len(list(self.connected_edges(pid)))>=self.port(pid).capacity())):
				raise PortError("capacity of port %s exceeded" % str(pid))

		eid = self.add_edge( (self.vertex(source_pid),self.vertex(target_pid)),eid)
		self.edge_property("_source_port")[eid] = source_pid
		self.edge_property("_target_port")[eid] = target_pid
		return eid

	
	def disconnect (self, eid) :
		"""
		remove edge
		"""
		self.remove_edge(eid)

	
	def add_vertex (self, vid=None) :
		vid=PropertyGraph.add_vertex(self,vid)
		self.vertex_property("_ports")[vid] = set()
		return vid

	add_vertex.__doc__ = PropertyGraph.add_vertex.__doc__

	
	def remove_vertex (self, vid) :
		for pid in list(self.ports(vid)) :
			self.remove_port(pid)
		PropertyGraph.remove_vertex(self,vid)
		
	remove_vertex.__doc__ = PropertyGraph.remove_vertex.__doc__
	

	def clear (self) :
		self._ports.clear()
		self._pid_generator = IdGenerator()
		PropertyGraph.clear(self)

	clear.__doc__ = PropertyGraph.clear.__doc__