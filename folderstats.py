"""
	This application recurses into a directory specified by the user and gathers various stats about everything it contains, such as the total length of audio, total lines of text etc. It has hopefully been set up to be extendable so that new file formats and aditional stats can be added easily. At this time, stats are intended to contain numerical values.
	Copyright Sam Tupy, MIT license (see the file license).
"""

import os, sys, threading, wx
import stats # Code for handling stats.
from stats import _all_stats # Load the stats themselves.

app = wx.App()

# Scans happen on multiple threads for performance, so we need to register a custom event type with wx so the main application can get a report about when a scan finishes or aborts.
EVT_SCAN_RESULT = wx.Window.NewControlId()
class scan_result_event(wx.PyEvent):
	def __init__(self, data):
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_SCAN_RESULT)
		self.data = data

# The lowest level of the app. Should I be subclassing wx.App here? IDK I'm new to wx.
class folderstats_frame(wx.Frame):
	def __init__(self, parent = None):
		wx.Frame.__init__(self, parent, title="Folderstats", size=(1024, 1024))
		self.main_panel = folderstats_panel(self)
		self.Connect(-1, -1, EVT_SCAN_RESULT, self.on_scan_result)
		self.Center()
		self.main_panel.Show()
		self.Show(True)
		self.scan_progress = 0
		self.scan_path = ""
		self.scan_threads = os.cpu_count()
		self.results = {}
	def scan_thread(self, dirs_this_thread):
		"""This thread scans a portion of the root folder structure provided by the user."""
		path = self.main_panel.dir_picker.GetPath()
		tree = self.main_panel.results_tree
		for root, dirs, files in os.walk(path):
			if self.scan_progress < 0:
				self.scan_progress += 1;
				if not self.scan_progress:
					wx.PostEvent(self, scan_result_event({"success": False}))
				return
			if root == path:
				dirs.clear()
				for d in dirs_this_thread: dirs.append(d)
			root_element = self.results[root]["wx_tree"]
			stats.increase_stat(root, self.results, "dir_count", len(dirs))
			for d in dirs:
				item_path = os.path.join(root, d)
				if item_path in self.results: continue
				self.results[item_path] = {"wx_tree": tree.AppendItem(root_element, d, data = item_path)}
			for f in files:
				stats.scan_file(os.path.join(root, f), self.results)
		self.scan_progress -= 1
		if not self.scan_progress:
			wx.PostEvent(self, scan_result_event({"success": True})) # Theoretically the last thread running 
	def scan(self, evt = None):
		"""Usually called directly by wx as a result of a button press, this function actually begins the scanning process by refreshing the tree view and divvying out directories to as many scan threads as possible based on os.cpu_count(). It also cancels a scan if one is already running."""
		if self.scan_progress > 0:
			self.scan_progress = -self.scan_progress # signal abort
			return
		tree = self.main_panel.results_tree
		path = self.main_panel.dir_picker.GetPath()
		tree.DeleteAllItems()
		p = os.path.split(path)
		if p[1] != "": p = p[1]
		else: p = p[0]
		root_element = tree.AddRoot(p, data = path)
		self.scan_threads = os.cpu_count()
		self.results = {path: {"wx_tree": root_element}}
		dirs = []
		# Quick hack to grab just directories.
		for r, d, f in os.walk(path):
			dirs = d
			break
		if "$RECYCLE.BIN" in dirs: dirs.remove("$RECYCLE.BIN")
		if "System Volume Information" in dirs: dirs.remove("System Volume Information")
		if len(dirs) < 1: return
		# We need to add the root directories to the tree now for sorting purposes, else they'll be added all sorts of out of order by the threading.
		for d in dirs:
			item_path = os.path.join(path, d)
			self.results[item_path] = {"wx_tree": tree.AppendItem(root_element, d, data = item_path)}
		if len(dirs) < self.scan_threads * 2: self.scan_threads = 1 #Too few items for multithreading here.
		self.scan_progress = self.scan_threads
		self.scan_path = path
		items_per_thread = int(len(dirs) / self.scan_threads)
		for i in range(self.scan_threads):
			if (i * items_per_thread) + items_per_thread >= len(dirs) or i == self.scan_threads -1: threading.Thread(target = self.scan_thread, args = (dirs[i * items_per_thread:],), daemon = True).start()
			else: threading.Thread(target = self.scan_thread, args = (dirs[i * items_per_thread:(i * items_per_thread) + items_per_thread],), daemon = True).start()
		self.main_panel.rescan_btn.SetLabel("Cancel")
	def on_scan_result(self, evt):
		"""Handler for our custom scan_result event."""
		# Scan either failed or succeeded, in any case reset the button label.
		self.main_panel.rescan_btn.SetLabel("&Scan")
		if not evt.data["success"]: return
		# We'll likely need more processing here.
	def select_result(self, evt):
		"""Called by wx upon a wx.EVT_TREE_SEL_CHANGED event, this function sets the contents of the results text field to the correct value based on the newly selected tree item."""
		if not evt.Item:
			self.main_panel.results_text.SetValue("")
			return
		path = self.main_panel.results_tree.GetItemData(evt.Item)
		if not path in self.results:
			self.main_panel.results_text.SetValue("")
			return
		self.main_panel.results_text.SetValue(stats.to_str(path, self.results))

class folderstats_panel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		results_sizer = wx.BoxSizer()
		tree_label = wx.StaticText(self, -1, "&Folder structure")
		self.results_tree = wx.TreeCtrl(self, name = "")
		self.results_tree.Bind(wx.EVT_TREE_SEL_CHANGED, parent.select_result, self.results_tree)
		text_label = wx.StaticText(self, -1, "&Results")
		self.results_text = wx.TextCtrl(self, style = wx.TE_MULTILINE | wx.TE_READONLY, size=(480, 120))
		results_sizer.Add(self.results_tree, 0, wx.ALL, 5)
		results_sizer.Add(self.results_text, 0, wx.ALL, 5)
		selection_sizer = wx.BoxSizer()
		self.dir_picker = wx.DirPickerCtrl(self, path=os.getcwd(), name = "Select a directory", message = "Select a directory")
		self.rescan_btn = wx.Button(self, wx.ID_ANY, "&Scan")
		self.rescan_btn.Bind(wx.EVT_BUTTON, parent.scan, self.rescan_btn)
		selection_sizer.Add(self.dir_picker, 0, wx.ALL, 5)
		selection_sizer.Add(self.rescan_btn, 0, wx.ALL, 5)
		results_sizer.Add(selection_sizer, 0, wx.ALL, 5)
		self.SetSizer(results_sizer)
		self.Hide()
		self.Fit()

main_window = folderstats_frame()
app.MainLoop()
