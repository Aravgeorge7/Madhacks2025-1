import { Node, Edge } from "reactflow";

export const initialNodes: Node[] = [
  // Smith Family - High Risk Person Nodes
  {
    id: "john-smith",
    type: "default",
    data: { label: "John Smith" },
    position: { x: 100, y: 100 },
    style: {
      background: "#ef4444",
      color: "#fff",
      border: "2px solid #dc2626",
      borderRadius: "8px",
      padding: "10px",
      fontWeight: "600",
    },
  },
  {
    id: "sarah-smith",
    type: "default",
    data: { label: "Sarah Smith" },
    position: { x: 300, y: 100 },
    style: {
      background: "#ef4444",
      color: "#fff",
      border: "2px solid #dc2626",
      borderRadius: "8px",
      padding: "10px",
      fontWeight: "600",
    },
  },
  {
    id: "mike-smith",
    type: "default",
    data: { label: "Mike Smith" },
    position: { x: 100, y: 250 },
    style: {
      background: "#ef4444",
      color: "#fff",
      border: "2px solid #dc2626",
      borderRadius: "8px",
      padding: "10px",
      fontWeight: "600",
    },
  },
  {
    id: "emma-smith",
    type: "default",
    data: { label: "Emma Smith" },
    position: { x: 300, y: 250 },
    style: {
      background: "#ef4444",
      color: "#fff",
      border: "2px solid #dc2626",
      borderRadius: "8px",
      padding: "10px",
      fontWeight: "600",
    },
  },
  // Shared Providers - High Risk
  {
    id: "dr-chen",
    type: "default",
    data: { label: "Dr. Chen" },
    position: { x: 500, y: 100 },
    style: {
      background: "#ef4444",
      color: "#fff",
      border: "2px solid #dc2626",
      borderRadius: "8px",
      padding: "10px",
      fontWeight: "600",
    },
  },
  {
    id: "attorney-rodriguez",
    type: "default",
    data: { label: "Attorney Rodriguez" },
    position: { x: 500, y: 250 },
    style: {
      background: "#ef4444",
      color: "#fff",
      border: "2px solid #dc2626",
      borderRadius: "8px",
      padding: "10px",
      fontWeight: "600",
    },
  },
  // IP Address - Gray
  {
    id: "ip-address",
    type: "default",
    data: { label: "192.168.1.50" },
    position: { x: 200, y: 400 },
    style: {
      background: "#6b7280",
      color: "#fff",
      border: "2px solid #4b5563",
      borderRadius: "8px",
      padding: "10px",
      fontWeight: "600",
    },
  },
];

export const initialEdges: Edge[] = [
  // All Smiths connected to Dr. Chen
  { id: "john-dr-chen", source: "john-smith", target: "dr-chen", animated: true },
  { id: "sarah-dr-chen", source: "sarah-smith", target: "dr-chen", animated: true },
  { id: "mike-dr-chen", source: "mike-smith", target: "dr-chen", animated: true },
  { id: "emma-dr-chen", source: "emma-smith", target: "dr-chen", animated: true },
  // All Smiths connected to Attorney Rodriguez
  { id: "john-attorney", source: "john-smith", target: "attorney-rodriguez", animated: true },
  { id: "sarah-attorney", source: "sarah-smith", target: "attorney-rodriguez", animated: true },
  { id: "mike-attorney", source: "mike-smith", target: "attorney-rodriguez", animated: true },
  { id: "emma-attorney", source: "emma-smith", target: "attorney-rodriguez", animated: true },
  // All Smiths connected to IP Address
  { id: "john-ip", source: "john-smith", target: "ip-address", animated: true },
  { id: "sarah-ip", source: "sarah-smith", target: "ip-address", animated: true },
  { id: "mike-ip", source: "mike-smith", target: "ip-address", animated: true },
  { id: "emma-ip", source: "emma-smith", target: "ip-address", animated: true },
];

