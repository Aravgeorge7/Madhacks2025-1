"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";

interface GraphNode {
  id: string;
  type: string;
  label: string;
  risk_score?: number;
  risk_category?: string;
  claimant_name?: string;
  status?: string;
  entity_value?: string;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  relationship: string;
}

interface ConnectionInfo {
  nodeId: string;
  nodeLabel: string;
  nodeType: string;
  connectionType: string;
  relationship: string;
  riskScore?: number;
  riskCategory?: string;
  claimantName?: string;
  sharedEntity?: string;
  sharedEntityType?: string;
  suspiciousReason?: string;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export default function RiskNetworkGraph3D() {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set());
  const [connectionDetails, setConnectionDetails] = useState<ConnectionInfo[]>([]);
  const [highlightedEdges, setHighlightedEdges] = useState<Set<string>>(new Set());
  const nodesRef = useRef<THREE.Group>(new THREE.Group());
  const edgesRef = useRef<THREE.Group>(new THREE.Group());
  const nodeMeshesRef = useRef<Map<string, THREE.Mesh>>(new Map());
  const edgeMeshesRef = useRef<Map<string, THREE.Line>>(new Map());

  // Fetch graph data from backend
  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/graph");
        if (!response.ok) throw new Error("Failed to fetch graph data");
        const data = await response.json();
        setGraphData(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching graph data:", error);
        setLoading(false);
      }
    };

    fetchGraphData();
  }, []);

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current || !graphData) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Scene with darker, cleaner background
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050505);
    scene.fog = new THREE.Fog(0x050505, 50, 200);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 10000);
    camera.position.set(0, 0, 50);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Better lighting setup - brighter to show colors
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 1.0);
    directionalLight1.position.set(50, 50, 50);
    directionalLight1.castShadow = false;
    scene.add(directionalLight1);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.6);
    directionalLight2.position.set(-50, -50, -50);
    scene.add(directionalLight2);

    // Add point lights for better depth and color
    const pointLight1 = new THREE.PointLight(0xffffff, 0.3, 100);
    pointLight1.position.set(30, 30, 30);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0xffffff, 0.3, 100);
    pointLight2.position.set(-30, -30, -30);
    scene.add(pointLight2);

    // Create graph visualization
    const nodesGroup = new THREE.Group();
    const edgesGroup = new THREE.Group();
    nodesRef.current = nodesGroup;
    edgesRef.current = edgesGroup;
    scene.add(nodesGroup);
    scene.add(edgesGroup);

    // Layout nodes in 3D space using force-directed layout
    const nodePositions: Map<string, THREE.Vector3> = new Map();
    const nodeObjects: Map<string, THREE.Mesh> = new Map();

    // Initialize positions in a larger sphere for better distribution
    const nodeCount = graphData.nodes.length;
    const radius = Math.max(30, Math.sqrt(nodeCount) * 2);
    
    graphData.nodes.forEach((node, index) => {
      // Use golden angle spiral for better distribution
      const theta = index * 2.399963229728653; // Golden angle in radians
      const y = (1 - (index / nodeCount) * 2) * radius;
      const radius_at_y = Math.sqrt(radius * radius - y * y);
      const x = Math.cos(theta) * radius_at_y;
      const z = Math.sin(theta) * radius_at_y;
      nodePositions.set(node.id, new THREE.Vector3(x, y, z));
    });

    // Simple force-directed layout simulation (reduced iterations for performance)
    for (let iteration = 0; iteration < 50; iteration++) {
      const forces = new Map<string, THREE.Vector3>();
      graphData.nodes.forEach((node) => {
        forces.set(node.id, new THREE.Vector3(0, 0, 0));
      });

      // Repulsion between nodes (optimized - only check nearby nodes)
      // For large graphs, use spatial hashing or limit comparisons
      const maxRepulsionChecks = Math.min(100, graphData.nodes.length);
      for (let i = 0; i < maxRepulsionChecks; i++) {
        const node1 = graphData.nodes[i];
        for (let j = i + 1; j < Math.min(i + 20, graphData.nodes.length); j++) {
          const node2 = graphData.nodes[j];
          const pos1 = nodePositions.get(node1.id)!;
          const pos2 = nodePositions.get(node2.id)!;
          const diff = new THREE.Vector3().subVectors(pos1, pos2);
          const distance = diff.length() || 0.1;
          if (distance < 10) { // Only apply force if nodes are close
            const force = 0.1 / (distance * distance);
            diff.normalize().multiplyScalar(force);
            forces.get(node1.id)!.add(diff);
            forces.get(node2.id)!.sub(diff);
          }
        }
      }

      // Attraction along edges
      graphData.edges.forEach((edge) => {
        const pos1 = nodePositions.get(edge.source);
        const pos2 = nodePositions.get(edge.target);
        if (pos1 && pos2) {
          const diff = new THREE.Vector3().subVectors(pos2, pos1);
          const distance = diff.length() || 0.1;
          const force = distance * 0.01;
          diff.normalize().multiplyScalar(force);
          forces.get(edge.source)!.add(diff);
          forces.get(edge.target)!.sub(diff);
        }
      });

      // Apply forces
      forces.forEach((force, nodeId) => {
        const pos = nodePositions.get(nodeId)!;
        pos.add(force.multiplyScalar(0.1));
        // Damping
        force.multiplyScalar(0.9);
      });
    }

    // Create node meshes - skip IP addresses
    graphData.nodes.forEach((node) => {
      // Skip IP address nodes
      if (node.type === "ip") return;

      const position = nodePositions.get(node.id)!;

      // Determine color based on node type and risk
      let color = 0x888888;
      let size = 1;
      let emissive = 0x000000;

      if (node.type === "claim") {
        if (node.risk_category === "high") {
          color = 0xff3333; // Bright red
          emissive = 0x330000; // Subtle red glow
          size = 2;
        } else if (node.risk_category === "medium") {
          color = 0xffaa00; // Orange
          emissive = 0x332200; // Subtle orange glow
          size = 1.5;
        } else {
          color = 0x33ff33; // Bright green
          emissive = 0x003300; // Subtle green glow
          size = 1;
        }
      } else if (node.type === "doctor") {
        color = 0x0088ff; // Bright blue
        emissive = 0x001133; // Subtle blue glow
        size = 1.2;
      } else if (node.type === "lawyer") {
        color = 0xff00ff; // Bright magenta
        emissive = 0x330033; // Subtle magenta glow
        size = 1.2;
      } else if (node.type === "person") {
        color = 0xa855f7; // Vibrant purple
        emissive = 0x3b0764; // Purple glow
        size = 1;
      }

      // Create sphere for node
      const geometry = new THREE.SphereGeometry(size, 16, 16);
      const material = new THREE.MeshPhongMaterial({
        color,
        emissive,
        emissiveIntensity: 0.3,
        shininess: 80,
        specular: 0x444444
      });
      const sphere = new THREE.Mesh(geometry, material);
      sphere.position.copy(position);
      sphere.userData = { node, originalColor: color, originalEmissive: emissive, originalMaterial: material };
      nodeObjects.set(node.id, sphere);
      nodeMeshesRef.current.set(node.id, sphere);
      nodesGroup.add(sphere);
    });

    // Create edges (connections) - limit to important connections for performance
    // Only show edges between claims (shared entities) and direct claim-entity connections
    // Skip IP-related edges
    const importantEdges = graphData.edges.filter((edge) => {
      // Skip IP-related edges
      if (edge.source.includes("ip_") || edge.target.includes("ip_")) {
        return false;
      }
      if (edge.type.includes("ip")) {
        return false;
      }
      // Show all claim-to-entity edges
      if (edge.source.startsWith("claim_") && !edge.target.startsWith("claim_")) {
        return true;
      }
      // Show shared entity connections (claims connected through same entity)
      if (edge.type.includes("shared")) {
        return true;
      }
      return false;
    });

    // Limit total edges for performance (show up to 3000 most important)
    const edgesToShow = importantEdges.slice(0, 3000);
    
    edgesToShow.forEach((edge) => {
      const pos1 = nodePositions.get(edge.source);
      const pos2 = nodePositions.get(edge.target);

      if (pos1 && pos2) {
        // Use smooth curve for better-looking lines
        const midPoint = new THREE.Vector3().addVectors(pos1, pos2).multiplyScalar(0.5);
        const distance = pos1.distanceTo(pos2);
        const curveHeight = Math.min(distance * 0.15, 5);
        midPoint.y += curveHeight;

        const curve = new THREE.QuadraticBezierCurve3(pos1, midPoint, pos2);
        const points = curve.getPoints(30);
        const geometry = new THREE.BufferGeometry().setFromPoints(points);

        // Beautiful gradient-like colors based on connection type
        let color = 0x3a4a5a;
        let opacity = 0.35;

        if (edge.type.includes("doctor")) {
          color = 0x00d4ff; // Bright cyan
          opacity = 0.6;
        } else if (edge.type.includes("lawyer")) {
          color = 0xff6bff; // Bright pink/magenta
          opacity = 0.6;
        } else if (edge.type.includes("ip")) {
          color = 0x7c8a9a; // Steel blue-gray
          opacity = 0.3;
        } else if (edge.type.includes("shared")) {
          color = 0xffa726; // Warm amber/orange
          opacity = 0.7;
        } else if (edge.type.includes("phone")) {
          color = 0x4caf50; // Green
          opacity = 0.5;
        } else if (edge.type.includes("address")) {
          color = 0x9c27b0; // Purple
          opacity = 0.5;
        } else if (edge.type.includes("bank") || edge.type.includes("account")) {
          color = 0xffeb3b; // Yellow/gold
          opacity = 0.5;
        }

        const material = new THREE.LineBasicMaterial({
          color,
          opacity,
          transparent: true,
        });
        const line = new THREE.Line(geometry, material);
        const edgeKey = `${edge.source}-${edge.target}`;
        line.userData = { edge, edgeKey, originalColor: color, originalOpacity: opacity };
        edgeMeshesRef.current.set(edgeKey, line);
        edgesGroup.add(line);
      }
    });

    // Mouse interaction
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let hoveredObject: THREE.Object3D | null = null;

    const onMouseMove = (event: MouseEvent) => {
      if (!container) return;
      
      const rect = container.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodesGroup.children, true);

      // Reset previous hover (only if not highlighted by search)
      if (hoveredObject) {
        const mesh = hoveredObject as THREE.Mesh;
        const nodeId = mesh.userData.node?.id;
        if (nodeId) {
          const isHighlighted = highlightedNodes.has(nodeId);
          if (!isHighlighted) {
            mesh.material = mesh.userData.originalMaterial;
            mesh.scale.set(1, 1, 1);
          }
        }
        hoveredObject = null;
        setSelectedNode(null);
      }

      // Highlight hovered node (only if not already highlighted by search)
      if (intersects.length > 0) {
        const object = intersects[0].object;
        if (object.userData.node && !object.userData.isLabel) {
          const mesh = object as THREE.Mesh;
          const nodeId = object.userData.node.id;
          const isHighlighted = highlightedNodes.has(nodeId);
          
          // Only highlight if not already highlighted by search
          if (!isHighlighted) {
            hoveredObject = object;
            const originalColor = mesh.userData.originalColor || 0x888888;
            mesh.userData.originalMaterial = mesh.material;
            mesh.material = new THREE.MeshPhongMaterial({
              color: originalColor,
              emissive: originalColor,
              emissiveIntensity: 0.8,
              shininess: 100,
              specular: 0xffffff
            });
            mesh.scale.set(1.3, 1.3, 1.3);
          }
          setSelectedNode(object.userData.node);
        }
      }
    };

    container.addEventListener("mousemove", onMouseMove);
    
    // Store highlightedNodes in closure for mouse handlers
    let currentHighlightedNodes = highlightedNodes;
    const updateHighlightedNodes = () => {
      currentHighlightedNodes = highlightedNodes;
    };

    // Camera controls (simple orbit)
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };

    const onMouseDown = (event: MouseEvent) => {
      isDragging = true;
      previousMousePosition = { x: event.clientX, y: event.clientY };
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    const onMouseDrag = (event: MouseEvent) => {
      if (!isDragging) return;

      const deltaX = event.clientX - previousMousePosition.x;
      const deltaY = event.clientY - previousMousePosition.y;

      const spherical = new THREE.Spherical();
      spherical.setFromVector3(camera.position);
      spherical.theta -= deltaX * 0.01;
      spherical.phi += deltaY * 0.01;
      spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));

      camera.position.setFromSpherical(spherical);
      camera.lookAt(0, 0, 0);

      previousMousePosition = { x: event.clientX, y: event.clientY };
    };

    container.addEventListener("mousedown", onMouseDown);
    container.addEventListener("mouseup", onMouseUp);
    container.addEventListener("mousemove", onMouseDrag);

    // Zoom with wheel
    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      const zoomSpeed = 0.1;
      const distance = camera.position.length();
      const newDistance = distance + event.deltaY * zoomSpeed;
      camera.position.normalize().multiplyScalar(Math.max(10, Math.min(200, newDistance)));
    };

    container.addEventListener("wheel", onWheel);

    // Animation loop
    const animate = () => {
      animationFrameRef.current = requestAnimationFrame(animate);

      // No auto-rotation - user controls all rotation
      
      renderer.render(scene, camera);
    };
    animate();

    // Cleanup
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      container.removeEventListener("mousemove", onMouseMove);
      container.removeEventListener("mousedown", onMouseDown);
      container.removeEventListener("mouseup", onMouseUp);
      container.removeEventListener("mousemove", onMouseDrag);
      container.removeEventListener("wheel", onWheel);
      if (renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [graphData]);

  // Handle search and highlight connected nodes
  useEffect(() => {
    if (!graphData || !searchQuery.trim()) {
      setHighlightedNodes(new Set());
      setHighlightedEdges(new Set());
      setConnectionDetails([]);
      // Reset all nodes to original appearance - show everything
      nodeMeshesRef.current.forEach((mesh) => {
        mesh.visible = true;
        const originalMaterial = mesh.userData.originalMaterial;
        if (originalMaterial) {
          mesh.material = originalMaterial;
          mesh.scale.set(1, 1, 1);
        }
      });
      // Reset all edges to original appearance - show everything
      edgeMeshesRef.current.forEach((line) => {
        line.visible = true;
        const material = line.material as THREE.LineBasicMaterial;
        material.color.setHex(line.userData.originalColor);
        material.opacity = line.userData.originalOpacity;
      });
      return;
    }

    const query = searchQuery.toLowerCase().trim();
    const matchingNodes = new Set<string>();
    const connectedNodes = new Set<string>();
    const connectedEdgeKeys = new Set<string>();
    const connections: ConnectionInfo[] = [];

    // Create node lookup map
    const nodeMap = new Map<string, GraphNode>();
    graphData.nodes.forEach((node) => {
      nodeMap.set(node.id, node);
    });

    // Find matching nodes
    graphData.nodes.forEach((node) => {
      const label = (node.label || "").toLowerCase();
      const claimant = (node.claimant_name || "").toLowerCase();
      const entity = (node.entity_value || "").toLowerCase();

      if (label.includes(query) || claimant.includes(query) || entity.includes(query)) {
        matchingNodes.add(node.id);
        connectedNodes.add(node.id);
      }
    });

    // Track shared entities between claims for suspicious connection detection
    const claimSharedEntities = new Map<string, { entityType: string; entityValue: string; claims: string[] }>();

    // First pass: collect all entity connections
    graphData.edges.forEach((edge) => {
      // If this connects a claim to an entity (doctor, lawyer, ip, person)
      if (edge.source.startsWith("claim_") && !edge.target.startsWith("claim_")) {
        const entityNode = nodeMap.get(edge.target);
        if (entityNode) {
          const key = edge.target;
          if (!claimSharedEntities.has(key)) {
            claimSharedEntities.set(key, {
              entityType: entityNode.type,
              entityValue: entityNode.entity_value || entityNode.label || "",
              claims: []
            });
          }
          claimSharedEntities.get(key)!.claims.push(edge.source);
        }
      }
    });

    // Find all nodes and edges connected to matching nodes
    graphData.edges.forEach((edge) => {
      const isSourceMatching = matchingNodes.has(edge.source);
      const isTargetMatching = matchingNodes.has(edge.target);

      if (isSourceMatching || isTargetMatching) {
        connectedNodes.add(edge.target);
        connectedNodes.add(edge.source);

        // Track connected edges
        const edgeKey1 = `${edge.source}-${edge.target}`;
        const edgeKey2 = `${edge.target}-${edge.source}`;
        connectedEdgeKeys.add(edgeKey1);
        connectedEdgeKeys.add(edgeKey2);

        // Get connected node info for the panel
        const matchingNodeId = isSourceMatching ? edge.source : edge.target;
        const connectedNodeId = isSourceMatching ? edge.target : edge.source;
        const connectedNode = nodeMap.get(connectedNodeId);
        const matchingNode = nodeMap.get(matchingNodeId);

        if (connectedNode && !matchingNodes.has(connectedNodeId)) {
          // Build meaningful connection info
          let connectionType = edge.type;
          let sharedEntity = "";
          let sharedEntityType = "";
          let suspiciousReason = "";

          // Determine what's being shared and why it's suspicious
          if (connectedNode.type === "doctor") {
            sharedEntityType = "Doctor/Provider";
            sharedEntity = connectedNode.entity_value || connectedNode.label || "";
            const sharedInfo = claimSharedEntities.get(connectedNodeId);
            const claimCount = sharedInfo?.claims.length || 1;
            if (claimCount > 1) {
              suspiciousReason = `Same doctor across ${claimCount} claims - potential provider fraud ring`;
            } else {
              suspiciousReason = "Medical provider connection";
            }
            connectionType = "Shared Doctor";
          } else if (connectedNode.type === "lawyer") {
            sharedEntityType = "Attorney";
            sharedEntity = connectedNode.entity_value || connectedNode.label || "";
            const sharedInfo = claimSharedEntities.get(connectedNodeId);
            const claimCount = sharedInfo?.claims.length || 1;
            if (claimCount > 1) {
              suspiciousReason = `Same attorney handling ${claimCount} claims - potential organized fraud`;
            } else {
              suspiciousReason = "Legal representation connection";
            }
            connectionType = "Shared Lawyer";
          } else if (connectedNode.type === "ip") {
            // Skip IP connections
            return;
          } else if (connectedNode.type === "person") {
            sharedEntityType = "Person";
            sharedEntity = connectedNode.entity_value || connectedNode.label || "";
            suspiciousReason = "Same claimant identity";
            connectionType = "Same Person";
          } else if (connectedNode.type === "claim") {
            sharedEntityType = "Related Claim";
            sharedEntity = connectedNode.label || "";
            // Find what entity connects these claims
            const riskLevel = connectedNode.risk_category || "unknown";
            if (riskLevel === "high") {
              suspiciousReason = "Connected to HIGH RISK claim - investigate relationship";
            } else if (riskLevel === "medium") {
              suspiciousReason = "Connected to medium risk claim";
            } else {
              suspiciousReason = "Related claim in network";
            }
            connectionType = "Linked Claim";
          }

          connections.push({
            nodeId: connectedNodeId,
            nodeLabel: connectedNode.label || connectedNode.entity_value || connectedNodeId,
            nodeType: connectedNode.type,
            connectionType: connectionType,
            relationship: edge.relationship || edge.type,
            riskScore: connectedNode.risk_score,
            riskCategory: connectedNode.risk_category,
            claimantName: connectedNode.claimant_name,
            sharedEntity: sharedEntity,
            sharedEntityType: sharedEntityType,
            suspiciousReason: suspiciousReason,
          });
        }
      }
    });

    setHighlightedNodes(connectedNodes);
    setHighlightedEdges(connectedEdgeKeys);
    // Remove duplicates and limit to 50 for better visibility
    const uniqueConnections = connections.filter(
      (conn, index, self) => index === self.findIndex((c) => c.nodeId === conn.nodeId)
    ).slice(0, 50);
    setConnectionDetails(uniqueConnections);

    // Update node appearances - HIDE non-connected nodes completely
    nodeMeshesRef.current.forEach((mesh, nodeId) => {
      const isHighlighted = connectedNodes.has(nodeId);
      const isMatching = matchingNodes.has(nodeId);
      const originalColor = mesh.userData.originalColor || 0x888888;

      if (isMatching) {
        // Matching nodes: Brilliant white/gold glow - THE SEARCHED ITEM
        mesh.visible = true;
        mesh.material = new THREE.MeshPhongMaterial({
          color: 0xffffff,
          emissive: 0xffd700, // Gold glow
          emissiveIntensity: 2.5,
          shininess: 200,
          specular: 0xffffff,
        });
        mesh.scale.set(4, 4, 4);
      } else if (isHighlighted) {
        // Connected nodes: Bright colored - CONNECTIONS
        mesh.visible = true;
        mesh.material = new THREE.MeshPhongMaterial({
          color: originalColor,
          emissive: originalColor,
          emissiveIntensity: 0.8,
          shininess: 150,
          specular: 0xffffff,
        });
        mesh.scale.set(2.5, 2.5, 2.5);
      } else {
        // HIDE non-connected nodes completely
        mesh.visible = false;
      }
    });

    // Update edge appearances - HIDE non-connected edges completely
    edgeMeshesRef.current.forEach((line, edgeKey) => {
      const isHighlighted = connectedEdgeKeys.has(edgeKey);

      if (isHighlighted) {
        // Show and highlight connected edges
        line.visible = true;
        const material = line.material as THREE.LineBasicMaterial;
        material.color.setHex(0x00ffff); // Bright cyan
        material.opacity = 1.0;
      } else {
        // HIDE non-connected edges completely
        line.visible = false;
      }
    });
  }, [searchQuery, graphData]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (!containerRef.current || !cameraRef.current || !rendererRef.current) return;
      
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      
      cameraRef.current.aspect = width / height;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(width, height);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <div className="text-slate-400">Loading graph data...</div>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
      {/* Search/Filter Input */}
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20">
        <div className={`bg-black/90 backdrop-blur-md rounded-xl px-5 py-4 shadow-2xl flex items-center gap-3 border-2 transition-all duration-300 ${searchQuery ? 'border-cyan-400 shadow-cyan-400/20' : 'border-slate-700'}`}>
          <svg className={`w-6 h-6 transition-colors ${searchQuery ? 'text-cyan-400' : 'text-slate-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search person, policy, doctor, lawyer..."
            className="bg-transparent text-white placeholder-slate-500 outline-none w-96 text-base font-medium"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="text-slate-400 hover:text-cyan-400 transition-colors text-xl font-bold"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      <div ref={containerRef} className="h-full w-full" />
      
      {/* Info panel - only show when NOT searching */}
      {selectedNode && !searchQuery && (
        <div className="absolute top-4 right-4 bg-black/90 backdrop-blur-md text-white p-4 rounded-xl shadow-2xl max-w-sm z-10 border border-slate-700">
          <h3 className="font-bold text-lg mb-3 text-cyan-400">{selectedNode.label}</h3>
          <div className="text-sm space-y-2">
            <div className="flex justify-between"><span className="text-slate-400">Type:</span> <span className="capitalize">{selectedNode.type}</span></div>
            {selectedNode.claimant_name && (
              <div className="flex justify-between"><span className="text-slate-400">Claimant:</span> <span>{selectedNode.claimant_name}</span></div>
            )}
            {selectedNode.risk_score !== undefined && (
              <div className="flex justify-between"><span className="text-slate-400">Risk Score:</span> <span className="font-semibold">{selectedNode.risk_score}</span></div>
            )}
            {selectedNode.risk_category && (
              <div className="flex justify-between"><span className="text-slate-400">Risk Level:</span> <span className={`font-semibold capitalize ${selectedNode.risk_category === 'high' ? 'text-red-400' : selectedNode.risk_category === 'medium' ? 'text-amber-400' : 'text-green-400'}`}>{selectedNode.risk_category}</span></div>
            )}
            {selectedNode.status && (
              <div className="flex justify-between"><span className="text-slate-400">Status:</span> <span className="capitalize">{selectedNode.status}</span></div>
            )}
            {selectedNode.entity_value && (
              <div className="flex justify-between"><span className="text-slate-400">Entity:</span> <span>{selectedNode.entity_value}</span></div>
            )}
          </div>
        </div>
      )}

      {/* Connection Details Panel - Shows when searching */}
      {searchQuery && connectionDetails.length > 0 && (
        <div className="absolute top-4 right-4 bg-black/95 backdrop-blur-md text-white p-5 rounded-2xl shadow-2xl w-[400px] z-20 border border-slate-700 max-h-[85vh] overflow-y-auto">
          <div className="flex items-center gap-3 mb-4 pb-3 border-b border-slate-700">
            <div className="w-2 h-2 rounded-full bg-cyan-400"></div>
            <h3 className="font-semibold text-base text-white">Connections Analysis</h3>
          </div>

          <div className="mb-4 p-3 bg-slate-800/50 rounded-lg">
            <div className="text-sm text-slate-400">
              Query: <span className="font-semibold text-white">{searchQuery}</span>
            </div>
            <div className="text-xs text-slate-500 mt-1">
              {connectionDetails.length} connection{connectionDetails.length !== 1 ? 's' : ''} found
            </div>
          </div>

          <div className="space-y-2">
            {connectionDetails.map((conn, index) => {
              // Get color based on node type
              let typeColor = "text-gray-300";
              let typeBg = "bg-slate-800/30";
              let borderColor = "border-slate-600";
              let riskBadge = null;

              if (conn.nodeType === "doctor") {
                typeColor = "text-cyan-400";
                typeBg = "bg-cyan-950/30";
                borderColor = "border-cyan-600";
              } else if (conn.nodeType === "lawyer") {
                typeColor = "text-pink-400";
                typeBg = "bg-pink-950/30";
                borderColor = "border-pink-600";
              } else if (conn.nodeType === "claim") {
                typeBg = "bg-slate-800/40";
                borderColor = "border-slate-600";
                if (conn.riskCategory === "high") {
                  typeColor = "text-red-400";
                  borderColor = "border-red-600";
                  riskBadge = <span className="text-[10px] font-semibold text-red-400 bg-red-950/50 px-1.5 py-0.5 rounded">HIGH</span>;
                } else if (conn.riskCategory === "medium") {
                  typeColor = "text-amber-400";
                  borderColor = "border-amber-600";
                  riskBadge = <span className="text-[10px] font-semibold text-amber-400 bg-amber-950/50 px-1.5 py-0.5 rounded">MED</span>;
                } else {
                  typeColor = "text-green-400";
                }
              } else if (conn.nodeType === "person") {
                typeColor = "text-purple-400";
                typeBg = "bg-purple-950/30";
                borderColor = "border-purple-600";
              }

              return (
                <div
                  key={`${conn.nodeId}-${index}`}
                  className={`p-3 rounded-lg ${typeBg} border-l-2 ${borderColor}`}
                >
                  {/* Name first, then details */}
                  <div className="mb-2">
                    {conn.nodeType === "claim" ? (
                      <>
                        <div className="flex items-center gap-2">
                          <span className={`font-semibold ${typeColor}`}>
                            {conn.claimantName || "Unknown Claimant"}
                          </span>
                          {riskBadge}
                        </div>
                        <div className="text-xs text-slate-500 mt-0.5">
                          {conn.nodeLabel}
                          {conn.riskScore !== undefined && (
                            <span className="ml-2">
                              Score: <span className={`font-semibold ${conn.riskScore >= 70 ? 'text-red-400' : conn.riskScore >= 40 ? 'text-amber-400' : 'text-green-400'}`}>{conn.riskScore}</span>
                            </span>
                          )}
                        </div>
                      </>
                    ) : (
                      <span className={`font-semibold ${typeColor}`}>
                        {conn.nodeLabel}
                      </span>
                    )}
                  </div>

                  {/* Connection type */}
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-[10px] uppercase tracking-wide text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded">
                      {conn.nodeType}
                    </span>
                    <span className="text-[10px] text-cyan-400 bg-cyan-950/50 px-1.5 py-0.5 rounded">
                      {conn.connectionType}
                    </span>
                  </div>

                  {/* Suspicious reason */}
                  {conn.suspiciousReason && (
                    <div className={`text-xs p-2 rounded ${conn.suspiciousReason.includes('HIGH RISK') ? 'bg-red-950/30 text-red-300' : 'bg-slate-900/50 text-slate-400'}`}>
                      {conn.suspiciousReason}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {connectionDetails.length >= 50 && (
            <div className="mt-3 pt-2 border-t border-slate-800 text-xs text-slate-500 text-center">
              Showing first 50
            </div>
          )}
        </div>
      )}

      {/* Controls hint - only show when NOT searching */}
      {!searchQuery && (
        <div className="absolute bottom-4 left-4 bg-black/80 backdrop-blur-md text-white p-3 rounded-xl text-xs shadow-xl border border-slate-700/50">
          <div className="text-slate-400 space-y-1">
            <div>Drag to rotate • Scroll to zoom</div>
            <div>Hover for details • Search to filter</div>
          </div>
        </div>
      )}

      {/* Legend - only show when NOT searching */}
      {!searchQuery && (
        <div className="absolute top-4 left-4 bg-black/80 backdrop-blur-md text-white p-4 rounded-xl text-xs border border-slate-700/50 shadow-xl">
          <div className="font-semibold mb-3 text-slate-400 uppercase tracking-wide text-[10px]">Node Types</div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span>High Risk Claim</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-amber-500"></div>
              <span>Medium Risk Claim</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
              <span>Low Risk Claim</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-cyan-400"></div>
              <span>Doctor/Provider</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-pink-400"></div>
              <span>Lawyer</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-purple-500"></div>
              <span>Person</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

