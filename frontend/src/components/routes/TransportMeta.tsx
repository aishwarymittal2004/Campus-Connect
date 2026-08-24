import { TrainFront, Bus, Car, Bike, PersonStanding, Route as RouteIcon, Plane } from "lucide-react";
import type { TransportType } from "@/types";

export const TRANSPORT_META: Record<
  TransportType,
  { label: string; icon: typeof TrainFront; colorClass: string; badgeVariant: TransportType }
> = {
  metro: { label: "Metro", icon: TrainFront, colorClass: "text-transit-metro", badgeVariant: "metro" },
  bus: { label: "Bus", icon: Bus, colorClass: "text-transit-bus", badgeVariant: "bus" },
  cab: { label: "Cab", icon: Car, colorClass: "text-transit-cab", badgeVariant: "cab" },
  auto: { label: "Auto", icon: Bike, colorClass: "text-transit-auto", badgeVariant: "auto" },
  walk: { label: "Walk", icon: PersonStanding, colorClass: "text-transit-walk", badgeVariant: "walk" },
  mixed: { label: "Mixed", icon: RouteIcon, colorClass: "text-transit-mixed", badgeVariant: "mixed" },
  train: { label: "Train", icon: TrainFront, colorClass: "text-blue-500", badgeVariant: "metro" as any },
  flight: { label: "Flight", icon: Plane, colorClass: "text-sky-500", badgeVariant: "metro" as any },
};
