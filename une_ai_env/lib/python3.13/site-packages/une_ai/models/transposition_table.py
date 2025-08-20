import uuid
import os
import json
from abc import ABC, abstractmethod
import logging


from une_ai.models import GraphNode

class TTable(ABC):

    ZOBRIST_TABLE_FILENAME = 'zobrist-table.json'
    TT_FILENAME = 'transposition-table.json'

    def __init__(self, saving_directory='./transposition-tables/', instance_id=None, verbose=False):
        if instance_id is None:
            self._instance_id = str(uuid.uuid1())
        else:
            self._instance_id = instance_id
        
        self._zobrist_table = None
        self._tt = None
        self._tt_keys = []

        self._saving_dir = saving_directory
        if not os.path.exists(self.get_saving_directory()):
            os.makedirs(self.get_saving_directory())
        
        self._zobrist_table_filename = os.path.join(self._saving_dir, self._instance_id, TTable.ZOBRIST_TABLE_FILENAME)
        self._tt_filename = os.path.join(self._saving_dir, self._instance_id, TTable.TT_FILENAME)

        self._verbose = verbose
        self._logger = None

        if self._verbose:
            logging.basicConfig()
            logging.root.setLevel(logging.NOTSET)
            self._logger = logging.getLogger("TTable({0})".format(self.get_instance_id()))

        self._init_zobrist_table()
        self._init_transposition_table()
    
    @abstractmethod
    def generate_zobrist_table(self):
        pass

    @abstractmethod
    def compute_hash(self, state):
        pass

    def set_verbose(self, is_verbose):
        self._verbose = is_verbose
    
    def size(self):
        return len(self._tt['transposition-table'].keys())
    
    def get_instance_id(self):
        return self._instance_id
    
    def get_zobrist_table_filename(self):
        return self._zobrist_table_filename
    
    def get_ttable_filename(self):
        return self._tt_filename
    
    def get_saving_directory(self):
        return os.path.join(self._saving_dir, self._instance_id)
    
    def log(self, message):
        if self._verbose:
            self._logger.info(message)
    
    def _init_zobrist_table(self):
        if os.path.exists(self._zobrist_table_filename):
            self.log("Found existing zobrist table, loading it")
            with open(self._zobrist_table_filename, 'r') as f:
                self._zobrist_table = json.load(f)
        else:
            self.log("Zobrist table not found, creating one")
            self._zobrist_table = self.generate_zobrist_table()
            with open(self._zobrist_table_filename, 'w') as f:
                json.dump(self._zobrist_table, f)
    
    def _init_transposition_table(self):
        if os.path.exists(self._tt_filename):
            self.log("Found existing transposition table, loading it")
            with open(self._tt_filename, 'r') as f:
                self._tt = json.load(f)
            self._tt_keys = list(self._tt['transposition-table'].keys())
        else:
            self.log("Transposition table not found, creating one")
            self._tt = {
                'transposition-table': {},
                'instance-id': self._instance_id,
                'saving-dir': self._saving_dir,
                'zobrist-table-file': self._zobrist_table_filename,
                'tt-file': self._tt_filename
            }
            self._save_to_file()
    
    def get_zobrist_table(self):
        if self._zobrist_table is None:
            self._init_zobrist_table()
        
        return self._zobrist_table.copy()
    
    def get_ttable(self):
        if self._tt is None:
            self._init_transposition_table()
        
        return self._tt.copy()
    
    def store_node(self, node, entry_dict):
        assert isinstance(node, GraphNode), "The parameter node must be an instance of GraphNode"
        assert isinstance(entry_dict, dict), "The parameter entry_dict must be a dictionary"
        assert self._tt is not None, "The transposition table was not initialised yet"

        state_hash = self.compute_hash(node.get_state())

        # check if the node state is already stored in the tt table
        any_changes = state_hash not in self._tt_keys
        if state_hash in self._tt_keys:
            cur_entry = self._tt['transposition-table'][state_hash]
            cur_entry_dict = cur_entry['dict-values']
            origin_keys = list(cur_entry_dict.keys()).sort()
            updated_keys = list(entry_dict.keys()).sort()
            if origin_keys == updated_keys:
                for k, value in cur_entry_dict.items():
                    if value != entry_dict[k]:
                        any_changes = True
                        break
        
        if any_changes:
            self.log("Storing new node with state hash '{0}', values = {1}".format(state_hash, entry_dict))
            if state_hash not in self._tt['transposition-table'].keys():
                self._tt['transposition-table'][state_hash] = {}
                self._tt_keys.append(state_hash)
            self._tt['transposition-table'][state_hash]['dict-values'] = entry_dict
            self._save_to_file()

    def lookup(self, node):
        assert isinstance(node, GraphNode), "The parameter node must be an instance of GraphNode"

        state_hash = self.compute_hash(node.get_state())

        if state_hash in self._tt_keys:
            # node state already stored, retrieve it
            tt = self.get_ttable()
            return tt['transposition-table'][state_hash]['dict-values']
        
        return None
    
    def _save_to_file(self):
        assert self._tt is not None, "The transposition table was not initialised yet"

        with open(self._tt_filename, 'w') as f:
            json.dump(self._tt, f)
            self.log("New version of the table successfully saved at '{0}' (size = {1})".format(self._tt_filename, self.size()))
    