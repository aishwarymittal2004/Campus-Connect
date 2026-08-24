import { useState } from "react";
import { Users, BarChart3, GraduationCap, Tag, Trash2, ShieldCheck, ShieldOff } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAdminAnalytics, useAdminUsers, useDeleteUser, useUpdateUserRole } from "@/hooks/useAdmin";
import { useColleges, useCreateCollege, useDeleteCollege } from "@/hooks/useColleges";
import { useCreateOffer, useDeleteOffer, useOffers } from "@/hooks/useOffers";
import { useToast } from "@/components/ui/toast";
import { getApiErrorMessage } from "@/lib/api-client";

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <CardContent className="p-5">
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="stat-mono mt-1 text-2xl font-bold">{value}</p>
      </CardContent>
    </Card>
  );
}

function AnalyticsTab() {
  const { data, isLoading } = useAdminAnalytics();
  if (isLoading || !data) return <Skeleton className="h-64 w-full rounded-xl" />;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Total Users" value={data.total_users} />
        <StatCard label="Students" value={data.total_students} />
        <StatCard label="Colleges" value={data.total_colleges} />
        <StatCard label="Route Searches" value={data.total_route_searches} />
        <StatCard label="Bookmarked Routes" value={data.total_bookmarked_routes} />
        <StatCard label="Reviews" value={data.total_reviews} />
        <StatCard label="Avg Rating" value={data.average_rating?.toFixed(1) ?? "—"} />
        <StatCard label="Active Offers" value={data.total_active_offers} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Transport Mode Breakdown</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {Object.entries(data.transport_type_breakdown).map(([mode, count]) => (
            <div key={mode} className="flex items-center justify-between text-sm">
              <span className="capitalize">{mode}</span>
              <span className="stat-mono font-medium">{count}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function UsersTab() {
  const { data: users, isLoading } = useAdminUsers();
  const updateRole = useUpdateUserRole();
  const deleteUser = useDeleteUser();
  const { toast } = useToast();

  if (isLoading) return <Skeleton className="h-64 w-full rounded-xl" />;

  return (
    <div className="space-y-2">
      {users?.map((u) => (
        <Card key={u.id}>
          <CardContent className="flex items-center justify-between gap-3 p-4">
            <div className="min-w-0">
              <p className="truncate font-medium">{u.name}</p>
              <p className="truncate text-xs text-muted-foreground">{u.email}</p>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <Badge variant={u.role === "admin" ? "metro" : "secondary"}>{u.role}</Badge>
              {!u.is_active && <Badge variant="destructive">Inactive</Badge>}
              <Button
                variant="ghost"
                size="icon"
                title={u.role === "admin" ? "Demote to student" : "Promote to admin"}
                onClick={() =>
                  updateRole.mutate(
                    { id: u.id, payload: { role: u.role === "admin" ? "student" : "admin" } },
                    { onError: (e) => toast({ title: "Update failed", description: getApiErrorMessage(e), variant: "error" }) }
                  )
                }
              >
                {u.role === "admin" ? <ShieldOff className="h-4 w-4" /> : <ShieldCheck className="h-4 w-4" />}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="text-destructive"
                onClick={() =>
                  deleteUser.mutate(u.id, {
                    onError: (e) => toast({ title: "Delete failed", description: getApiErrorMessage(e), variant: "error" }),
                  })
                }
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function CollegesTab() {
  const { data: colleges, isLoading } = useColleges();
  const createCollege = useCreateCollege();
  const deleteCollege = useDeleteCollege();
  const { toast } = useToast();
  const [form, setForm] = useState({ name: "", city: "", latitude: "", longitude: "" });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createCollege.mutate(
      { name: form.name, city: form.city, latitude: parseFloat(form.latitude), longitude: parseFloat(form.longitude) },
      {
        onSuccess: () => {
          setForm({ name: "", city: "", latitude: "", longitude: "" });
          toast({ title: "College created", variant: "success" });
        },
        onError: (e) => toast({ title: "Couldn't create college", description: getApiErrorMessage(e), variant: "error" }),
      }
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Add a college</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreate} className="grid gap-3 sm:grid-cols-2">
            <div>
              <Label className="mb-1.5 block text-xs">Name</Label>
              <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div>
              <Label className="mb-1.5 block text-xs">City</Label>
              <Input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} required />
            </div>
            <div>
              <Label className="mb-1.5 block text-xs">Latitude</Label>
              <Input
                type="number"
                step="any"
                value={form.latitude}
                onChange={(e) => setForm({ ...form, latitude: e.target.value })}
                required
              />
            </div>
            <div>
              <Label className="mb-1.5 block text-xs">Longitude</Label>
              <Input
                type="number"
                step="any"
                value={form.longitude}
                onChange={(e) => setForm({ ...form, longitude: e.target.value })}
                required
              />
            </div>
            <Button type="submit" className="sm:col-span-2" disabled={createCollege.isPending}>
              Add College
            </Button>
          </form>
        </CardContent>
      </Card>

      {isLoading && <Skeleton className="h-40 w-full rounded-xl" />}
      <div className="space-y-2">
        {colleges?.map((c) => (
          <Card key={c.id}>
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <p className="font-medium">{c.name}</p>
                <p className="text-xs text-muted-foreground">{c.city}</p>
              </div>
              <Button variant="ghost" size="icon" className="text-destructive" onClick={() => deleteCollege.mutate(c.id)}>
                <Trash2 className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

function OffersTab() {
  const { data: offers, isLoading } = useOffers();
  const createOffer = useCreateOffer();
  const deleteOffer = useDeleteOffer();
  const { toast } = useToast();
  const [form, setForm] = useState({ platform: "zomato", category: "food", title: "", discount: "", url: "" });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    createOffer.mutate(form as never, {
      onSuccess: () => {
        setForm({ platform: "zomato", category: "food", title: "", discount: "", url: "" });
        toast({ title: "Offer created", variant: "success" });
      },
      onError: (e) => toast({ title: "Couldn't create offer", description: getApiErrorMessage(e), variant: "error" }),
    });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Add an offer</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreate} className="grid gap-3 sm:grid-cols-2">
            <div>
              <Label className="mb-1.5 block text-xs">Platform</Label>
              <select
                className="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
                value={form.platform}
                onChange={(e) => setForm({ ...form, platform: e.target.value })}
              >
                <option value="zomato">Zomato</option>
                <option value="swiggy">Swiggy</option>
                <option value="amazon">Amazon</option>
                <option value="flipkart">Flipkart</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <Label className="mb-1.5 block text-xs">Category</Label>
              <select
                className="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm"
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
              >
                <option value="food">Food</option>
                <option value="shopping">Shopping</option>
                <option value="student">Student</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <Label className="mb-1.5 block text-xs">Title</Label>
              <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
            </div>
            <div>
              <Label className="mb-1.5 block text-xs">Discount label</Label>
              <Input
                placeholder="e.g. 20% OFF"
                value={form.discount}
                onChange={(e) => setForm({ ...form, discount: e.target.value })}
                required
              />
            </div>
            <div>
              <Label className="mb-1.5 block text-xs">URL</Label>
              <Input value={form.url} onChange={(e) => setForm({ ...form, url: e.target.value })} required />
            </div>
            <Button type="submit" className="sm:col-span-2" disabled={createOffer.isPending}>
              Add Offer
            </Button>
          </form>
        </CardContent>
      </Card>

      {isLoading && <Skeleton className="h-40 w-full rounded-xl" />}
      <div className="space-y-2">
        {offers?.map((o) => (
          <Card key={o.id}>
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <p className="font-medium">{o.title}</p>
                <p className="text-xs capitalize text-muted-foreground">
                  {o.platform} · {o.discount}
                </p>
              </div>
              <Button variant="ghost" size="icon" className="text-destructive" onClick={() => deleteOffer.mutate(o.id)}>
                <Trash2 className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

export function AdminDashboardPage() {
  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="font-display text-2xl font-bold tracking-tight">Admin Dashboard</h1>
      <p className="mt-1 text-muted-foreground">Manage colleges, offers, users, and view platform analytics.</p>

      <Tabs defaultValue="analytics" className="mt-6">
        <TabsList className="flex-wrap">
          <TabsTrigger value="analytics">
            <BarChart3 className="mr-1.5 h-4 w-4" /> Analytics
          </TabsTrigger>
          <TabsTrigger value="users">
            <Users className="mr-1.5 h-4 w-4" /> Users
          </TabsTrigger>
          <TabsTrigger value="colleges">
            <GraduationCap className="mr-1.5 h-4 w-4" /> Colleges
          </TabsTrigger>
          <TabsTrigger value="offers">
            <Tag className="mr-1.5 h-4 w-4" /> Offers
          </TabsTrigger>
        </TabsList>
        <TabsContent value="analytics">
          <AnalyticsTab />
        </TabsContent>
        <TabsContent value="users">
          <UsersTab />
        </TabsContent>
        <TabsContent value="colleges">
          <CollegesTab />
        </TabsContent>
        <TabsContent value="offers">
          <OffersTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
