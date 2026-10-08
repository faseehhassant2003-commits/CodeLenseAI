import { useState } from "react";

function buildTree(files) {
  const root = {};

  files.forEach((file) => {
    const parts = file.path.split("/");

    let current = root;

    parts.forEach((part, index) => {
      const isFile = index === parts.length - 1;

      if (!current[part]) {
        current[part] = {
          type: isFile ? "file" : "folder",
          name: part,
          path: isFile ? file.path : null,
          children: isFile ? null : {},
        };
      }

      if (!isFile) {
        current = current[part].children;
      }
    });
  });

  return root;
}

function TreeNode({
  name,
  node,
  level,
  openFile,
}) {
  const [expanded, setExpanded] = useState(false);

  if (node.type === "file") {
    return (
      <div
        className="file-tree-item file-item"
        style={{ paddingLeft: `${level * 18}px` }}
        onClick={() => openFile(node.path)}
      >
        <span>📄</span>
        <span>{name}</span>
      </div>
    );
  }

  return (
    <div>
      <div
        className="file-tree-item folder-item"
        style={{ paddingLeft: `${level * 18}px` }}
        onClick={() => setExpanded(!expanded)}
      >
        <span>{expanded ? "📂" : "📁"}</span>
        <span>{name}</span>
      </div>

      {expanded &&
        Object.entries(node.children).map(
          ([childName, childNode]) => (
            <TreeNode
              key={childName}
              name={childName}
              node={childNode}
              level={level + 1}
              openFile={openFile}
            />
          )
        )}
    </div>
  );
}

function FileTree({ files, openFile }) {
  const tree = buildTree(files);

  return (
    <div className="file-tree">
      {Object.entries(tree).map(
        ([name, node]) => (
          <TreeNode
            key={name}
            name={name}
            node={node}
            level={0}
            openFile={openFile}
          />
        )
      )}
    </div>
  );
}

export default FileTree;