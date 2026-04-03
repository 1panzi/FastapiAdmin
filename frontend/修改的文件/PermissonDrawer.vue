<!-- 角色授权 -->
<template>
  <!-- 权限分配弹窗 -->
  <el-dialog
    v-model="dialogVisible"
    :title="'【' + props.roleName + '】权限分配'"
    :width="dialogWidth"
    :fullscreen="isMobile"
    top="5vh"
    destroy-on-close
  >
    <!-- 顶部工具栏 -->
    <div class="flex items-center justify-between flex-wrap gap-y-2 mb-4">
      <!-- 左侧：角色级数据权限 -->
      <div class="flex items-center gap-2">
        <span class="text-sm font-bold whitespace-nowrap">角色数据权限:</span>
        <el-select v-model="permissionState.data_scope" size="small" style="width: 160px">
          <el-option :value="1" label="仅本人数据权限" />
          <el-option :value="2" label="本部门数据权限" />
          <el-option :value="3" label="本部门及以下数据权限" />
          <el-option :value="4" label="全部数据权限" />
          <el-option :value="5" label="自定义数据权限" />
        </el-select>
        <el-button
          v-if="permissionState.data_scope === 5"
          size="small"
          type="primary"
          @click="openRoleDeptDialog"
        >
          选择部门({{ roleDeptIds.length }})
        </el-button>
      </div>
      <!-- 右侧：搜索 + 操作 -->
      <div class="flex items-center gap-2">
        <el-input
          v-model="filterText"
          size="small"
          placeholder="菜单名称"
          clearable
          style="width: 150px"
          :prefix-icon="Search"
        />
        <el-button size="small" plain @click="toggleExpandAll">
          {{ isAllExpanded ? "收缩" : "展开" }}
        </el-button>
        <el-button size="small" plain @click="toggleSelectAll">
          {{ isAllSelected ? "取消全选" : "全选" }}
        </el-button>
        <el-checkbox v-model="parentChildLinked" size="small">父子联动</el-checkbox>
        <el-tooltip placement="bottom">
          <template #content>
            如果只需勾选菜单权限，不需要勾选子菜单或者按钮权限，请关闭父子联动
          </template>
          <el-icon class="ml-1 color-[--el-color-primary] cursor-pointer">
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </div>

    <!-- 权限列表 -->
    <div class="permission-list-wrapper">
      <!-- 表头 -->
      <div class="permission-header">
        <div class="col-name">菜单名称</div>
        <div class="col-scope">数据权限</div>
        <div class="col-buttons">按钮权限</div>
      </div>

      <!-- 可滚动内容区 -->
      <div class="permission-body">
        <template v-if="visibleFlatList.length">
          <div
            v-for="node in visibleFlatList"
            :key="node.id"
            :class="['permission-row', node.type === 1 ? 'directory-row' : 'menu-row']"
          >
            <!-- === 目录行 (type=1) === -->
            <template v-if="node.type === 1">
              <div class="col-name" :style="{ paddingLeft: node.depth * 24 + 'px' }">
                <el-icon class="expand-icon cursor-pointer mr-1" @click="toggleExpand(node.id)">
                  <ArrowDown v-if="expandedDirs.has(node.id)" />
                  <ArrowRight v-else />
                </el-icon>
                <el-checkbox
                  :model-value="isDirChecked(node)"
                  :indeterminate="isDirIndeterminate(node)"
                  :disabled="node.disabled"
                  @change="(val: any) => toggleDirCheck(node, !!val)"
                />
                <span class="font-bold ml-1">{{ node.name }}</span>
              </div>
              <div class="col-scope"></div>
              <div class="col-buttons"></div>
            </template>

            <!-- === 菜单行 (type=2) === -->
            <template v-else-if="node.type === 2">
              <div class="col-name" :style="{ paddingLeft: node.depth * 24 + 'px' }">
                <el-checkbox
                  :model-value="checkedMenuIds.has(node.id)"
                  :disabled="node.disabled"
                  @change="(val: any) => toggleMenuCheck(node, !!val)"
                />
                <span class="ml-1">{{ node.name }}</span>
              </div>
              <div class="col-scope">
                <el-select
                  v-model="menuDataScopes[node.id]"
                  size="small"
                  placeholder="继承默认"
                  clearable
                  style="width: 130px"
                  :disabled="!checkedMenuIds.has(node.id)"
                  @clear="handleMenuScopeClear(node.id)"
                >
                  <el-option :value="1" label="仅本人" />
                  <el-option :value="2" label="本部门" />
                  <el-option :value="3" label="本部门及以下" />
                  <el-option :value="4" label="全部" />
                  <el-option :value="5" label="自定义" />
                </el-select>
                <el-button
                  v-if="menuDataScopes[node.id] === 5 && checkedMenuIds.has(node.id)"
                  size="small"
                  type="primary"
                  link
                  class="ml-1"
                  @click="openMenuDeptDialog(node.id)"
                >
                  选择部门({{ (menuDeptSelections[node.id] || []).length }})
                </el-button>
              </div>
              <div class="col-buttons">
                <template v-if="node.buttons.length">
                  <span class="btn-label">按钮权限:</span>
                  <span
                    v-for="btn in node.buttons"
                    :key="btn.id"
                    class="btn-item"
                  >
                    <el-checkbox
                      :model-value="checkedMenuIds.has(btn.id)"
                      :disabled="btn.disabled"
                      @change="(val: any) => toggleBtnCheck(btn, node, !!val)"
                    />
                    <span class="btn-name">{{ btn.name }}</span>
                    <el-icon
                      v-if="checkedMenuIds.has(btn.id)"
                      class="btn-scope-icon"
                      @click.stop="openBtnScopeDialog(btn.id)"
                    >
                      <Setting />
                    </el-icon>
                  </span>
                </template>
              </div>
            </template>

            <!-- === 外链行 (type=4) === -->
            <template v-else>
              <div class="col-name" :style="{ paddingLeft: node.depth * 24 + 'px' }">
                <el-checkbox
                  :model-value="checkedMenuIds.has(node.id)"
                  :disabled="node.disabled"
                  @change="(val: any) => toggleMenuCheck(node, !!val)"
                />
                <span class="ml-1">{{ node.name }}</span>
              </div>
              <div class="col-scope"></div>
              <div class="col-buttons"></div>
            </template>
          </div>
        </template>
        <el-empty v-else :image-size="80" description="暂无数据" />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSave">确 定</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 角色级自定义部门选择弹窗 -->
  <el-dialog
    v-model="roleDeptDialogVisible"
    title="角色自定义数据权限部门"
    width="400px"
    append-to-body
    destroy-on-close
  >
    <el-tree
      ref="roleDeptTreeRef"
      node-key="value"
      show-checkbox
      :data="deptTreeData"
      default-expand-all
      :highlight-current="true"
      style="max-height: 50vh; overflow-y: auto"
    />
    <template #footer>
      <el-button @click="roleDeptDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="confirmRoleDeptSelection">确定</el-button>
    </template>
  </el-dialog>

  <!-- 菜单级自定义部门选择弹窗 -->
  <el-dialog
    v-model="menuDeptDialogVisible"
    title="菜单自定义数据权限部门"
    width="400px"
    append-to-body
    destroy-on-close
  >
    <el-tree
      ref="menuDeptTreeRef"
      node-key="value"
      show-checkbox
      :data="deptTreeData"
      default-expand-all
      :highlight-current="true"
      style="max-height: 50vh; overflow-y: auto"
    />
    <template #footer>
      <el-button @click="menuDeptDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="confirmMenuDeptSelection">确定</el-button>
    </template>
  </el-dialog>

  <!-- 按钮级数据权限配置弹窗（齿轮⚙） -->
  <el-dialog
    v-model="btnScopeDialogVisible"
    title="按钮数据权限配置"
    width="450px"
    append-to-body
    destroy-on-close
  >
    <el-form label-width="100px">
      <el-form-item label="数据权限">
        <el-select v-model="tempBtnScope" placeholder="继承默认" clearable style="width: 100%">
          <el-option :value="1" label="仅本人" />
          <el-option :value="2" label="本部门" />
          <el-option :value="3" label="本部门及以下" />
          <el-option :value="4" label="全部" />
          <el-option :value="5" label="自定义" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="tempBtnScope === 5" label="选择部门">
        <el-tree
          ref="btnDeptTreeRef"
          node-key="value"
          show-checkbox
          :data="deptTreeData"
          default-expand-all
          :highlight-current="true"
          style="max-height: 40vh; overflow-y: auto; width: 100%"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="btnScopeDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="confirmBtnScope">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { listToTree, formatTree } from "@/utils/common";
import RoleAPI, {
  MenuDataScopeItem,
  permissionDataType,
  permissionDeptType,
  permissionMenuType,
} from "@/api/module_system/role";
import DeptAPI from "@/api/module_system/dept";
import MenuAPI from "@/api/module_system/menu";
import type { TreeInstance } from "element-plus";
import { useAppStore } from "@/store/modules/app.store";
import { DeviceEnum } from "@/enums/settings/device.enum";
import { useUserStore } from "@/store";
import { Search, Setting, ArrowDown, ArrowRight, QuestionFilled } from "@element-plus/icons-vue";

// ==================== Props / Emits ====================

const props = defineProps({
  roleName: { type: String, required: true },
  roleId: { type: Number, required: true },
  modelValue: { type: Boolean, required: true },
});
const emit = defineEmits(["update:modelValue", "saved"]);

// ==================== 基础状态 ====================

const appStore = useAppStore();
const isMobile = computed(() => appStore.device !== DeviceEnum.DESKTOP);
const dialogWidth = computed(() => (isMobile.value ? "95%" : "90%"));

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

const loading = ref(false);
const parentChildLinked = ref(false);
const filterText = ref("");
const isAllExpanded = ref(true);

// ==================== 数据状态 ====================

const deptTreeData = ref<any[]>([]);
const permissionState = ref<permissionDataType>({
  role_ids: [],
  menu_ids: [],
  data_scope: 1,
  dept_ids: [],
  menu_data_scopes: [],
});

// 菜单/按钮级数据权限
const menuDataScopes = ref<Record<number, number | null>>({});
const menuDeptSelections = ref<Record<number, number[]>>({});
const checkedMenuIds = ref<Set<number>>(new Set());

// 角色级部门
const roleDeptIds = ref<number[]>([]);

// ==================== 预处理菜单树 ====================

interface ProcessedMenuNode {
  id: number;
  name: string;
  type: number;
  depth: number;
  parentId: number | null;
  disabled: boolean;
  hasChildren: boolean;
  children: ProcessedMenuNode[];
  buttons: ProcessedMenuNode[];
  allDescendantIds: number[];
}

const menuTree = ref<ProcessedMenuNode[]>([]);
// 节点ID → 父节点ID 映射
const parentMap = ref<Record<number, number>>({});
// 所有节点ID → 节点 映射
const nodeMap = ref<Map<number, ProcessedMenuNode>>(new Map());
// 所有目录ID集合
const allDirIds = ref<Set<number>>(new Set());

function processMenuTree(
  rawNodes: any[],
  depth: number = 0,
  parentId: number | null = null
): ProcessedMenuNode[] {
  const result: ProcessedMenuNode[] = [];

  for (const raw of rawNodes) {
    const rawChildren: any[] = raw.children || [];
    // 分离按钮子节点和非按钮子节点
    const buttonChildren = rawChildren.filter((c: any) => c.type === 3);
    const nonButtonChildren = rawChildren.filter((c: any) => c.type !== 3);

    // 递归处理非按钮子节点
    const children = processMenuTree(nonButtonChildren, depth + 1, raw.id);

    // 处理按钮子节点
    const buttons: ProcessedMenuNode[] = buttonChildren.map((btn: any) => {
      const btnNode: ProcessedMenuNode = {
        id: btn.id,
        name: btn.name,
        type: btn.type,
        depth: depth + 1,
        parentId: raw.id,
        disabled: btn.status === "1" || btn.status === false,
        hasChildren: false,
        children: [],
        buttons: [],
        allDescendantIds: [],
      };
      parentMap.value[btn.id] = raw.id;
      nodeMap.value.set(btn.id, btnNode);
      return btnNode;
    });

    // 收集所有后代ID
    const allDescendantIds: number[] = [];
    for (const child of children) {
      allDescendantIds.push(child.id, ...child.allDescendantIds);
    }
    for (const btn of buttons) {
      allDescendantIds.push(btn.id);
    }

    const node: ProcessedMenuNode = {
      id: raw.id,
      name: raw.name,
      type: raw.type,
      depth,
      parentId,
      disabled: raw.status === "1" || raw.status === false,
      hasChildren: children.length > 0,
      children,
      buttons,
      allDescendantIds,
    };

    if (parentId !== null) {
      parentMap.value[raw.id] = parentId;
    }
    nodeMap.value.set(raw.id, node);

    if (raw.type === 1) {
      allDirIds.value.add(raw.id);
    }

    result.push(node);
  }

  return result;
}

// ==================== 展开/折叠 ====================

const expandedDirs = ref<Set<number>>(new Set());

function toggleExpand(dirId: number) {
  if (expandedDirs.value.has(dirId)) {
    expandedDirs.value.delete(dirId);
  } else {
    expandedDirs.value.add(dirId);
  }
  // 触发响应式更新
  expandedDirs.value = new Set(expandedDirs.value);
}

function toggleExpandAll() {
  if (isAllExpanded.value) {
    expandedDirs.value = new Set();
  } else {
    expandedDirs.value = new Set(allDirIds.value);
  }
  isAllExpanded.value = !isAllExpanded.value;
}

// ==================== 可见节点列表 ====================

const visibleFlatList = computed<ProcessedMenuNode[]>(() => {
  const result: ProcessedMenuNode[] = [];
  const keyword = filterText.value.trim().toLowerCase();

  function flatten(nodes: ProcessedMenuNode[]) {
    for (const node of nodes) {
      // type=3 按钮不独立成行
      if (node.type === 3) continue;

      if (keyword) {
        // 搜索模式：匹配名称或有匹配后代的节点可见
        if (nodeMatchesFilter(node, keyword)) {
          result.push(node);
          if (node.children.length > 0) {
            flatten(node.children);
          }
        }
      } else {
        // 正常模式：受展开状态控制
        result.push(node);
        if (node.type === 1 && expandedDirs.value.has(node.id) && node.children.length > 0) {
          flatten(node.children);
        } else if (node.type !== 1 && node.children.length > 0) {
          flatten(node.children);
        }
      }
    }
  }

  flatten(menuTree.value);
  return result;
});

function nodeMatchesFilter(node: ProcessedMenuNode, keyword: string): boolean {
  if (node.name.toLowerCase().includes(keyword)) return true;
  // 检查按钮
  for (const btn of node.buttons) {
    if (btn.name.toLowerCase().includes(keyword)) return true;
  }
  // 检查子节点
  for (const child of node.children) {
    if (nodeMatchesFilter(child, keyword)) return true;
  }
  return false;
}

// ==================== 勾选逻辑 ====================

function isChecked(id: number): boolean {
  return checkedMenuIds.value.has(id);
}

function isDirChecked(node: ProcessedMenuNode): boolean {
  if (node.allDescendantIds.length === 0) return checkedMenuIds.value.has(node.id);
  return (
    checkedMenuIds.value.has(node.id) &&
    node.allDescendantIds.every((id) => checkedMenuIds.value.has(id))
  );
}

function isDirIndeterminate(node: ProcessedMenuNode): boolean {
  if (node.allDescendantIds.length === 0) return false;
  const checkedCount = node.allDescendantIds.filter((id) => checkedMenuIds.value.has(id)).length;
  const selfChecked = checkedMenuIds.value.has(node.id);
  if (checkedCount === 0 && !selfChecked) return false;
  if (checkedCount === node.allDescendantIds.length && selfChecked) return false;
  return checkedCount > 0 || selfChecked;
}

// 全选/取消全选
const isAllSelected = computed(() => {
  if (nodeMap.value.size === 0) return false;
  for (const [id] of nodeMap.value) {
    if (!checkedMenuIds.value.has(id)) return false;
  }
  return true;
});

function toggleSelectAll() {
  const newSet = new Set<number>();
  if (!isAllSelected.value) {
    for (const [id, node] of nodeMap.value) {
      if (!node.disabled) {
        newSet.add(id);
      }
    }
  }
  checkedMenuIds.value = newSet;
}

// 勾选目录
function toggleDirCheck(node: ProcessedMenuNode, checked: boolean) {
  const newSet = new Set(checkedMenuIds.value);

  if (checked) {
    newSet.add(node.id);
    if (parentChildLinked.value) {
      for (const id of node.allDescendantIds) {
        const n = nodeMap.value.get(id);
        if (n && !n.disabled) newSet.add(id);
      }
      cascadeCheckParents(node.id, newSet);
    }
  } else {
    newSet.delete(node.id);
    if (parentChildLinked.value) {
      for (const id of node.allDescendantIds) {
        newSet.delete(id);
        cleanNodeScope(id);
      }
    }
    cleanNodeScope(node.id);
  }

  checkedMenuIds.value = newSet;
}

// 勾选菜单
function toggleMenuCheck(node: ProcessedMenuNode, checked: boolean) {
  const newSet = new Set(checkedMenuIds.value);

  if (checked) {
    newSet.add(node.id);
    if (parentChildLinked.value) {
      // 自动勾选所有按钮
      for (const btn of node.buttons) {
        if (!btn.disabled) newSet.add(btn.id);
      }
      // 自动勾选所有子节点后代
      for (const id of node.allDescendantIds) {
        const n = nodeMap.value.get(id);
        if (n && !n.disabled) newSet.add(id);
      }
      cascadeCheckParents(node.id, newSet);
    }
  } else {
    newSet.delete(node.id);
    cleanNodeScope(node.id);
    if (parentChildLinked.value) {
      for (const btn of node.buttons) {
        newSet.delete(btn.id);
        cleanNodeScope(btn.id);
      }
      for (const id of node.allDescendantIds) {
        newSet.delete(id);
        cleanNodeScope(id);
      }
      cascadeUncheckParents(node.id, newSet);
    }
  }

  checkedMenuIds.value = newSet;
}

// 勾选按钮
function toggleBtnCheck(btn: ProcessedMenuNode, parentNode: ProcessedMenuNode, checked: boolean) {
  const newSet = new Set(checkedMenuIds.value);

  if (checked) {
    newSet.add(btn.id);
    if (parentChildLinked.value) {
      // 自动勾选父菜单和祖先目录
      newSet.add(parentNode.id);
      cascadeCheckParents(parentNode.id, newSet);
    }
  } else {
    newSet.delete(btn.id);
    cleanNodeScope(btn.id);
    if (parentChildLinked.value) {
      cascadeUncheckParents(btn.id, newSet);
    }
  }

  checkedMenuIds.value = newSet;
}

// 向上级联勾选父节点
function cascadeCheckParents(nodeId: number, set: Set<number>) {
  let pid = parentMap.value[nodeId];
  while (pid !== undefined) {
    const parentNode = nodeMap.value.get(pid);
    if (parentNode && !parentNode.disabled) {
      set.add(pid);
    }
    pid = parentMap.value[pid];
  }
}

// 向上级联取消父节点（如果所有子节点都已取消）
function cascadeUncheckParents(nodeId: number, set: Set<number>) {
  let pid = parentMap.value[nodeId];
  while (pid !== undefined) {
    const parentNode = nodeMap.value.get(pid);
    if (!parentNode) break;
    // 如果父节点的所有后代都没被选中，则取消父节点
    const anyChildChecked = parentNode.allDescendantIds.some((id) => set.has(id));
    if (!anyChildChecked) {
      set.delete(pid);
    }
    pid = parentMap.value[pid];
  }
}

// 清除节点的数据权限配置
function cleanNodeScope(nodeId: number) {
  delete menuDataScopes.value[nodeId];
  delete menuDeptSelections.value[nodeId];
}

// ==================== 数据权限弹窗 ====================

// --- 角色级部门弹窗 ---
const roleDeptDialogVisible = ref(false);
const roleDeptTreeRef = ref<TreeInstance>();

function openRoleDeptDialog() {
  roleDeptDialogVisible.value = true;
  nextTick(() => {
    roleDeptTreeRef.value?.setCheckedKeys(roleDeptIds.value);
  });
}

function confirmRoleDeptSelection() {
  if (roleDeptTreeRef.value) {
    roleDeptIds.value = roleDeptTreeRef.value.getCheckedKeys().map((k: any) => Number(k));
  }
  roleDeptDialogVisible.value = false;
}

// --- 菜单级部门弹窗 ---
const menuDeptDialogVisible = ref(false);
const menuDeptTreeRef = ref<TreeInstance>();
const currentMenuDeptMenuId = ref<number | null>(null);

function openMenuDeptDialog(menuId: number) {
  currentMenuDeptMenuId.value = menuId;
  menuDeptDialogVisible.value = true;
  nextTick(() => {
    const existingDepts = menuDeptSelections.value[menuId] || [];
    menuDeptTreeRef.value?.setCheckedKeys(existingDepts);
  });
}

function confirmMenuDeptSelection() {
  if (currentMenuDeptMenuId.value != null && menuDeptTreeRef.value) {
    menuDeptSelections.value[currentMenuDeptMenuId.value] = menuDeptTreeRef.value
      .getCheckedKeys()
      .map((k: any) => Number(k));
  }
  menuDeptDialogVisible.value = false;
}

// --- 按钮级数据权限弹窗（齿轮⚙） ---
const btnScopeDialogVisible = ref(false);
const currentBtnScopeId = ref<number | null>(null);
const tempBtnScope = ref<number | null>(null);
const btnDeptTreeRef = ref<TreeInstance>();

function openBtnScopeDialog(btnId: number) {
  currentBtnScopeId.value = btnId;
  tempBtnScope.value = menuDataScopes.value[btnId] ?? null;
  btnScopeDialogVisible.value = true;
  nextTick(() => {
    if (btnDeptTreeRef.value && tempBtnScope.value === 5) {
      const existingDepts = menuDeptSelections.value[btnId] || [];
      btnDeptTreeRef.value.setCheckedKeys(existingDepts);
    }
  });
}

function confirmBtnScope() {
  if (currentBtnScopeId.value != null) {
    const btnId = currentBtnScopeId.value;
    if (tempBtnScope.value != null) {
      menuDataScopes.value[btnId] = tempBtnScope.value;
      if (tempBtnScope.value === 5 && btnDeptTreeRef.value) {
        menuDeptSelections.value[btnId] = btnDeptTreeRef.value
          .getCheckedKeys()
          .map((k: any) => Number(k));
      } else {
        delete menuDeptSelections.value[btnId];
      }
    } else {
      delete menuDataScopes.value[btnId];
      delete menuDeptSelections.value[btnId];
    }
  }
  btnScopeDialogVisible.value = false;
}

// 清除菜单级数据范围
function handleMenuScopeClear(menuId: number) {
  delete menuDataScopes.value[menuId];
  delete menuDeptSelections.value[menuId];
}

// ==================== 初始化 ====================

const init = async () => {
  loading.value = true;

  try {
    // 获取全部部门树
    const deptResponse = await DeptAPI.listDept();
    deptTreeData.value = formatTree(listToTree(deptResponse.data.data));

    // 获取全部菜单树
    const menuResponse = await MenuAPI.listMenu();
    const rawTree = listToTree(menuResponse.data.data);

    // 预处理菜单树
    parentMap.value = {};
    nodeMap.value = new Map();
    allDirIds.value = new Set();
    menuTree.value = processMenuTree(rawTree);

    // 默认全部展开
    expandedDirs.value = new Set(allDirIds.value);
    isAllExpanded.value = true;

    // 获取角色详情
    const roleResponse = await RoleAPI.detailRole(props.roleId);

    // 更新权限状态
    const menuIds = roleResponse.data.data.menus?.map((menu: any) => menu.id) || [];
    const deptIds = roleResponse.data.data.depts?.map((dept: any) => dept.id) || [];
    const dataScopeItems: MenuDataScopeItem[] =
      roleResponse.data.data.menu_data_scopes || [];

    permissionState.value = {
      role_ids: [props.roleId],
      menu_ids: menuIds,
      data_scope: roleResponse.data.data.data_scope || 1,
      dept_ids: deptIds,
      menu_data_scopes: dataScopeItems,
    };

    // 回显已勾选菜单
    checkedMenuIds.value = new Set(menuIds);

    // 角色级部门
    roleDeptIds.value = [...deptIds];

    // 回显菜单级数据权限
    menuDataScopes.value = {};
    menuDeptSelections.value = {};
    for (const item of dataScopeItems) {
      menuDataScopes.value[item.menu_id] = item.data_scope;
      if (item.data_scope === 5 && item.dept_ids?.length) {
        menuDeptSelections.value[item.menu_id] = [...item.dept_ids];
      }
    }

    // 判断是否应开启父子联动
    parentChildLinked.value = detectParentChildLinked(menuIds);
  } catch (error: any) {
    ElMessage.error("获取权限数据失败: " + error.message);
  } finally {
    loading.value = false;
  }
};

// 检测已有权限数据是否满足父子联动模式
function detectParentChildLinked(menuIds: number[]): boolean {
  if (!menuIds.length) return false;
  const idSet = new Set(menuIds);

  for (const id of menuIds) {
    const node = nodeMap.value.get(id);
    if (!node) continue;

    // 检查所有后代
    if (node.allDescendantIds.length > 0) {
      const allDescChecked = node.allDescendantIds.every((did) => idSet.has(did));
      if (!allDescChecked) {
        const anyDescChecked = node.allDescendantIds.some((did) => idSet.has(did));
        if (anyDescChecked) return false;
      }
    }

    // 检查父节点是否选中
    const pid = parentMap.value[id];
    if (pid !== undefined && !idSet.has(pid)) {
      return false;
    }
  }

  return true;
}

// ==================== 保存 ====================

async function handleSave() {
  try {
    if (props.roleId === 1) {
      ElMessage.warning("系统默认角色，不可操作");
      return;
    }
    loading.value = true;

    const checkedIds = [...checkedMenuIds.value];

    // 构建菜单级数据权限列表
    const menuDataScopeList: MenuDataScopeItem[] = [];
    
    // ✅ 遍历所有已勾选的菜单，包括被清空的配置
    for (const menuId of checkedMenuIds.value) {
      const scope = menuDataScopes.value[menuId];
      
      // 如果有配置且不为 null，提交实际值；否则提交 null 表示清除
      menuDataScopeList.push({
        menu_id: menuId,
        data_scope: scope ?? null,  // key 点：被清空的菜单会提交 null
        dept_ids: scope === 5 ? menuDeptSelections.value[menuId] || [] : [],
      });
    }

    const submitData: permissionDataType = {
      role_ids: [props.roleId],
      menu_ids: checkedIds,
      data_scope: permissionState.value.data_scope,
      dept_ids: permissionState.value.data_scope === 5 ? roleDeptIds.value : [],
      menu_data_scopes: menuDataScopeList,
    };

    await RoleAPI.setPermission(submitData);

    // 更新全局用户状态
    const userStore = useUserStore();
    await userStore.getUserInfo();

    dialogVisible.value = false;
    emit("saved");
  } catch (error: any) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

// ==================== 生命周期 ====================

onMounted(async () => {
  await init();
});
</script>

<style lang="scss" scoped>
.permission-list-wrapper {
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: hidden;
  max-height: calc(80vh - 200px);
  display: flex;
  flex-direction: column;
}

.permission-header {
  display: flex;
  align-items: center;
  background-color: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
  font-weight: bold;
  font-size: 13px;
  color: var(--el-text-color-primary);
  position: sticky;
  top: 0;
  z-index: 10;
  padding: 8px 12px;
  flex-shrink: 0;
}

.permission-body {
  overflow-y: auto;
  flex: 1;
}

.permission-row {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  min-height: 40px;
  transition: background-color 0.15s;

  &:hover {
    background-color: var(--el-fill-color-lighter);
  }

  &:last-child {
    border-bottom: none;
  }
}

.directory-row {
  background-color: var(--el-fill-color-lighter);

  &:hover {
    background-color: var(--el-fill-color-light);
  }
}

.col-name {
  width: 220px;
  min-width: 180px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.col-scope {
  width: 260px;
  min-width: 220px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.col-buttons {
  flex: 1;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px 4px;
  min-width: 0;
}

.btn-label {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-right: 4px;
  white-space: nowrap;
}

.btn-item {
  display: inline-flex;
  align-items: center;
  margin-right: 8px;
  white-space: nowrap;
}

.btn-name {
  margin-left: 2px;
  font-size: 13px;
}

.btn-scope-icon {
  margin-left: 2px;
  cursor: pointer;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  transition: color 0.15s;

  &:hover {
    color: var(--el-color-primary);
  }
}

.expand-icon {
  font-size: 14px;
  transition: transform 0.15s;
}
</style>
