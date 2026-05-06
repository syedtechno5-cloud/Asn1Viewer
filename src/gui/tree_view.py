"""Tree View Widget for hierarchical ASN.1 structure display"""
from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QMenu, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import QTimer
from typing import Optional, Dict
from ..parser.asn1_types import ASN1Node


class ASN1TreeWidget(QTreeWidget):
    """
    Tree widget displaying ASN.1 structure hierarchically
    Emits signals when nodes are selected
    """

    node_selected = pyqtSignal(ASN1Node)
    context_menu_requested = pyqtSignal(ASN1Node, object)

    # How many children to materialise per batch (keeps UI responsive)
    BATCH_SIZE = 500

    # Custom item-data role used to tag "Load more" items
    # (Qt.ItemDataRole.UserRole == 256, so 257 is safe)
    _LOAD_MORE_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_node: Optional[ASN1Node] = None
        self.node_map: Dict[int, ASN1Node] = {}
        self.item_counter = 0

        self.setHeaderLabels(['Tag'])
        self.setColumnCount(1)
        self.setRootIsDecorated(True)
        self.setUniformRowHeights(True)  # faster paint when all rows same height
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemExpanded.connect(self._on_item_expanded)
        self.itemClicked.connect(self._on_item_clicked)  # handles "Load more"

        self.search_filter = ""
        self.filtered_nodes_set = set()
    
    def load_asn1_tree(self, root_node: ASN1Node):
        """Load ASN.1 tree for display."""
        self.setUpdatesEnabled(False)
        try:
            self.clear()
            self.node_map.clear()
            self.item_counter = 0
            self.root_node = root_node

            if root_node:
                self._add_node_recursive(root_node, None)
                if self.topLevelItemCount() > 0:
                    self.expandItem(self.topLevelItem(0))

            self.resizeColumnToContents(0)
        finally:
            self.setUpdatesEnabled(True)
    
    # Foreground colours per tag class: UNIVERSAL, APPLICATION, CONTEXT, PRIVATE
    _TAG_CLASS_COLORS = [
        None,                    # UNIVERSAL  – default (black / system theme)
        QColor(0,  90, 200),    # APPLICATION – blue
        QColor(140, 80,  0),    # CONTEXT     – amber/brown
        QColor(130,  0, 130),   # PRIVATE     – purple
    ]

    def _add_node_recursive(self, node: ASN1Node, parent_item: Optional[QTreeWidgetItem]):
        """Add a node to the tree with a lazy-loading placeholder for its children."""
        display_name = node.get_display_name()
        # Use full tag hex (e.g. 0x5F20 for multi-byte APPLICATION tags)
        tag_str = f"{display_name} [{node.tag.get_hex_str()}]"
        if not node.children and 0 < node.length <= 32:
            tag_str += f"  = {node.get_preview()}"

        item = QTreeWidgetItem()
        item.setText(0, tag_str)

        self.item_counter += 1
        self.node_map[id(item)] = node
        item.setData(0, Qt.ItemDataRole.UserRole, id(item))

        font = QFont()
        if node.tag.constructed:
            font.setBold(True)
        item.setFont(0, font)

        color = self._TAG_CLASS_COLORS[node.tag.tag_class]
        if color is not None:
            item.setForeground(0, color)

        if parent_item is None:
            self.addTopLevelItem(item)
        else:
            parent_item.addChild(item)

        # Lazy: add a placeholder so Qt shows the expand arrow
        if node.children:
            placeholder = QTreeWidgetItem()
            placeholder.setText(0, "...")
            item.addChild(placeholder)
    
    def _on_selection_changed(self):
        """Handle tree item selection change"""
        selected_items = self.selectedItems()
        if selected_items:
            item = selected_items[0]
            item_id = id(item)
            if item_id in self.node_map:
                node = self.node_map[item_id]
                self.node_selected.emit(node)
    
    def _on_context_menu(self, pos):
        """Handle right-click context menu"""
        item = self.itemAt(pos)
        if item:
            item_id = id(item)
            if item_id in self.node_map:
                node = self.node_map[item_id]
                self.context_menu_requested.emit(node, self.mapToGlobal(pos))
    
    def _on_item_expanded(self, item: QTreeWidgetItem):
        """
        Handle item expansion for lazy loading
        
        Args:
            item: The expanded item
        """
        # Check if this item has a placeholder child
        if item.childCount() == 1 and item.child(0).text(0) == "...":
            # Remove placeholder
            item.takeChild(0)
            
            # Get the node
            item_id = id(item)
            if item_id in self.node_map:
                node = self.node_map[item_id]
                
                # Add actual children asynchronously to avoid blocking UI
                if node.children:
                    self.setCursor(Qt.CursorShape.WaitCursor)
                    # Capture loop variables explicitly to avoid late-binding closure issues
                    QTimer.singleShot(0, lambda i=item, c=node.children: self._expand_node_children(i, c))

    def _expand_node_children(self, item: QTreeWidgetItem, children: list):
        """Start batched population of a node's children."""
        self._add_children_batch(item, children, 0)

    def _add_children_batch(self, parent_item: QTreeWidgetItem, children: list, offset: int):
        """
        Add up to BATCH_SIZE children starting at *offset*.
        If more remain, append a clickable 'Load more' sentinel item so the UI
        never blocks waiting for thousands of items to be constructed at once.
        """
        self.setUpdatesEnabled(False)
        try:
            batch = children[offset:offset + self.BATCH_SIZE]
            for child_node in batch:
                self._add_node_recursive(child_node, parent_item)

            next_offset = offset + len(batch)
            remaining = len(children) - next_offset
            if remaining > 0:
                load_item = QTreeWidgetItem()
                load_item.setText(
                    0,
                    f"[ Load {min(self.BATCH_SIZE, remaining):,} more"
                    f" … ({remaining:,} children remaining) ]"
                )
                load_item.setForeground(0, QColor(100, 100, 200))
                # Store enough info to continue loading on click
                load_item.setData(0, self._LOAD_MORE_ROLE,
                                  (parent_item, children, next_offset))
                parent_item.addChild(load_item)
        finally:
            self.setUpdatesEnabled(True)
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def _on_item_clicked(self, item: QTreeWidgetItem, _=None):
        """Handle clicks on 'Load more' sentinel items."""
        load_data = item.data(0, self._LOAD_MORE_ROLE)
        if load_data is None:
            return
        parent_item, children, offset = load_data
        # Remove the sentinel before adding the next batch
        parent_item.removeChild(item)
        self.setCursor(Qt.CursorShape.WaitCursor)
        self._add_children_batch(parent_item, children, offset)

    def get_selected_node(self) -> Optional[ASN1Node]:
        """Get currently selected node"""
        selected_items = self.selectedItems()
        if selected_items:
            item = selected_items[0]
            item_id = id(item)
            if item_id in self.node_map:
                return self.node_map[item_id]
        return None
    
    def select_node_by_offset(self, offset: int) -> Optional[ASN1Node]:
        """
        Find and select node by byte offset
        
        Args:
            offset: Byte offset in file
        
        Returns:
            Selected node or None
        """
        if not self.root_node:
            return None
        
        def find_node(node: ASN1Node) -> Optional[ASN1Node]:
            if node.tag_offset <= offset < node.value_offset + node.length:
                if node.children:
                    for child in node.children:
                        result = find_node(child)
                        if result:
                            return result
                return node
            return None
        
        found_node = find_node(self.root_node)
        if found_node:
            self._select_node_item(found_node)
            return found_node
        return None
    
    def _select_node_item(self, node: ASN1Node):
        """
        Find and select the tree item for a node
        
        Args:
            node: Node to select
        """
        def find_item(item: QTreeWidgetItem) -> Optional[QTreeWidgetItem]:
            item_id = id(item)
            if item_id in self.node_map and self.node_map[item_id] is node:
                return item
            
            for i in range(item.childCount()):
                result = find_item(item.child(i))
                if result:
                    return result
            return None
        
        # Search from all top-level items
        for i in range(self.topLevelItemCount()):
            result = find_item(self.topLevelItem(i))
            if result:
                self.setCurrentItem(result)
                self.scrollToItem(result)
                return
    
    def filter_nodes(self, search_term: str):
        """
        Filter tree to show only matching nodes
        
        Args:
            search_term: Search term (used for name/tag filtering)
        """
        self.search_filter = search_term.lower()
        
        # Rebuild tree with filtering
        if self.root_node:
            self.clear()
            self.node_map.clear()
            self._add_filtered_nodes(self.root_node, None, search_term.lower())
        
        # Expand all visible items
        for i in range(self.topLevelItemCount()):
            self._expand_all_items(self.topLevelItem(i))
    
    def _add_filtered_nodes(self, node: ASN1Node, parent_item: Optional[QTreeWidgetItem], 
                           search_term: str):
        """
        Add nodes matching filter to tree
        
        Args:
            node: Current node
            parent_item: Parent item
            search_term: Filter term (lowercase)
        """
        # Check if node matches
        node_name = node.get_display_name().lower()
        node_tag = f"0x{node.tag.raw_byte:02x}"
        matches = search_term in node_name or search_term in node_tag
        
        # Check if any children match
        has_matching_children = any(
            self._node_matches_filter(child, search_term) 
            for child in node.children
        )
        
        if matches or has_matching_children:
            display_name = node.get_display_name()
            tag_str = f"{display_name} [{node.tag.get_hex_str()}]"
            if not node.children and 0 < node.length <= 32:
                tag_str += f"  = {node.get_preview()}"

            item = QTreeWidgetItem()
            item.setText(0, tag_str)

            self.item_counter += 1
            self.node_map[id(item)] = node
            item.setData(0, Qt.ItemDataRole.UserRole, id(item))

            color = self._TAG_CLASS_COLORS[node.tag.tag_class]
            if color is not None:
                item.setForeground(0, color)

            if parent_item is None:
                self.addTopLevelItem(item)
            else:
                parent_item.addChild(item)

            if node.children:
                for child in node.children:
                    self._add_filtered_nodes(child, item, search_term)
    
    def _node_matches_filter(self, node: ASN1Node, search_term: str) -> bool:
        """
        Check if node or any descendant matches filter
        
        Args:
            node: Node to check
            search_term: Filter term
        
        Returns:
            True if matches
        """
        # Search by tag number
        tag_str = f"#{node.tag.tag_number}"
        
        if search_term in tag_str:
            return True
        
        return any(self._node_matches_filter(child, search_term) for child in node.children)
    
    def _expand_all_items(self, item: QTreeWidgetItem):
        """Recursively expand all items"""
        self.expandItem(item)
        for i in range(item.childCount()):
            self._expand_all_items(item.child(i))
