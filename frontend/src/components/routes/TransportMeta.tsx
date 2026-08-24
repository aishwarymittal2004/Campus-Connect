import {
  TrainFront,
  Bus,
  Car,
  Bike,
  PersonStanding,
  Route as RouteIcon,
  Plane,
} from "lucide-react";
import type { TransportType } from "@/types";

type BadgeVariant =
  | "default"
  | "secondary"
  | "outline"
  | "destructive"
  | "accent";

export const TRANSPORT_META: Record<
  TransportType,
  {
    label: string;
    icon: typeof TrainFront;
    colorClass: string;
    badgeVariant: BadgeVariant;
  }
> = {
  metro: {
    label: "Metro",
    icon: TrainFront,
    colorClass: "text-transit-metro",
    badgeVariant: "default",
  },

  bus: {
    label: "Bus",
    icon: Bus,
    colorClass: "text-transit-bus",
    badgeVariant: "secondary",
  },

  cab: {
    label: "Cab",
    icon: Car,
    colorClass: "text-transit-cab",
    badgeVariant: "outline",
  },

  auto: {
    label: "Auto",
    icon: Bike,
    colorClass: "text-transit-auto",
    badgeVariant: "secondary",
  },

  walk: {
    label: "Walk",
    icon: PersonStanding,
    colorClass: "text-transit-walk",
    badgeVariant: "outline",
  },

  mixed: {
    label: "Mixed",
    icon: RouteIcon,
    colorClass: "text-transit-mixed",
    badgeVariant: "accent",
  },

  train: {
    label: "Train",
    icon: TrainFront,
    colorClass: "text-blue-500",
    badgeVariant: "secondary",
  },

  flight: {
    label: "Flight",
    icon: Plane,
    colorClass: "text-sky-500",
    badgeVariant: "accent",
  },
};