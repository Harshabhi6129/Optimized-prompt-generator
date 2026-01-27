# Component Showcase

Quick reference for all UI components with visual examples.

## Button Variants

```tsx
// Primary action
<Button variant="default">Save Changes</Button>

// Dangerous action
<Button variant="destructive">Delete Account</Button>

// Secondary action
<Button variant="outline">Cancel</Button>

// Subtle action
<Button variant="ghost">View Details</Button>

// Link style
<Button variant="link">Learn More</Button>

// Icon button
<Button variant="ghost" size="icon"><X /></Button>
```

## Input Types

```tsx
// Text input
<Input type="text" placeholder="Enter your name" />

// Email with validation
<Input type="email" placeholder="email@example.com" />

// Password
<Input type="password" placeholder="••••••••" />

// Number
<Input type="number" min={0} max={100} />

// Disabled
<Input disabled value="Read only" />
```

## Textarea

```tsx
// Basic
<Textarea placeholder="Enter description..." />

// With rows
<Textarea rows={10} />

// Custom height
<Textarea className="min-h-[200px]" />
```

## Card Layouts

```tsx
// Simple card
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Card content goes here</p>
  </CardContent>
</Card>

// Full card
<Card>
  <CardHeader>
    <CardTitle>Settings</CardTitle>
    <CardDescription>Manage your account settings</CardDescription>
  </CardHeader>
  <CardContent>
    <Input placeholder="Username" />
  </CardContent>
  <CardFooter className="justify-between">
    <Button variant="outline">Cancel</Button>
    <Button>Save</Button>
  </CardFooter>
</Card>
```

## Checkbox Examples

```tsx
// With label
<Checkbox label="Accept terms and conditions" />

// Controlled
<Checkbox 
  checked={isChecked} 
  onChange={(e) => setIsChecked(e.target.checked)}
/>

// Disabled
<Checkbox label="Disabled option" disabled />
```

## Radio Group

```tsx
// Basic usage
<RadioGroup
  name="size"
  options={[
    { label: "Small", value: "sm" },
    { label: "Medium", value: "md" },
    { label: "Large", value: "lg" }
  ]}
  value={size}
  onChange={setSize}
/>

// With default value
<RadioGroup
  name="theme"
  options={[
    { label: "Light", value: "light" },
    { label: "Dark", value: "dark" },
    { label: "System", value: "system" }
  ]}
  value="system"
/>
```

## Slider

```tsx
// Basic slider
<Slider value={50} onChange={setValue} />

// With range
<Slider min={0} max={100} step={5} value={volume} />

// With label
<div>
  <label>Volume: {volume}%</label>
  <Slider value={volume} onChange={setVolume} />
</div>
```

## Badge Variants

```tsx
// Status badges
<Badge variant="default">Active</Badge>
<Badge variant="secondary">Pending</Badge>
<Badge variant="destructive">Error</Badge>
<Badge variant="outline">Draft</Badge>

// Count badges
<Badge>{unreadCount}</Badge>

// With icons
<Badge><CheckCircle className="w-3 h-3 mr-1" />Verified</Badge>
```

## Complete Form Example

```tsx
function UserForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    bio: '',
    role: 'user',
    notifications: false,
    volume: 50
  });

  return (
    <Card className="max-w-2xl">
      <CardHeader>
        <CardTitle>User Profile</CardTitle>
        <CardDescription>Update your profile information</CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Text inputs */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Name</label>
          <Input 
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            placeholder="John Doe"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Email</label>
          <Input 
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            placeholder="john@example.com"
          />
        </div>

        {/* Textarea */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Bio</label>
          <Textarea 
            value={formData.bio}
            onChange={(e) => setFormData({...formData, bio: e.target.value})}
            placeholder="Tell us about yourself..."
            rows={4}
          />
        </div>

        {/* Radio group */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Role</label>
          <RadioGroup
            name="role"
            options={[
              { label: "User", value: "user" },
              { label: "Admin", value: "admin" },
              { label: "Moderator", value: "moderator" }
            ]}
            value={formData.role}
            onChange={(value) => setFormData({...formData, role: value})}
          />
        </div>

        {/* Checkbox */}
        <Checkbox 
          label="Enable email notifications"
          checked={formData.notifications}
          onChange={(e) => setFormData({...formData, notifications: e.target.checked})}
        />

        {/* Slider */}
        <div className="space-y-2">
          <label className="text-sm font-medium">
            Notification Volume: {formData.volume}%
          </label>
          <Slider 
            value={formData.volume}
            onChange={(value) => setFormData({...formData, volume: value})}
            min={0}
            max={100}
            step={10}
          />
        </div>
      </CardContent>

      <CardFooter className="justify-between">
        <Button variant="outline">Cancel</Button>
        <Button>Save Changes</Button>
      </CardFooter>
    </Card>
  );
}
```

## Layout Patterns

### Grid of Cards
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <Card>
    <CardHeader>
      <CardTitle>Card 1</CardTitle>
    </CardHeader>
    <CardContent>Content</CardContent>
  </Card>
  {/* More cards... */}
</div>
```

### Form with Sections
```tsx
<div className="space-y-6">
  <Card>
    <CardHeader>
      <CardTitle>Personal Information</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <Input placeholder="Name" />
      <Input placeholder="Email" />
    </CardContent>
  </Card>

  <Card>
    <CardHeader>
      <CardTitle>Preferences</CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <Checkbox label="Option 1" />
      <Checkbox label="Option 2" />
    </CardContent>
  </Card>
</div>
```

### Action Bar
```tsx
<div className="flex items-center justify-between">
  <div className="flex gap-2">
    <Badge>3 selected</Badge>
  </div>
  <div className="flex gap-2">
    <Button variant="outline">Cancel</Button>
    <Button variant="destructive">Delete</Button>
    <Button>Save</Button>
  </div>
</div>
```

## Responsive Design

All components are responsive by default. Use Tailwind breakpoints:

```tsx
<Button className="w-full md:w-auto">
  Responsive Button
</Button>

<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Responsive grid */}
</div>
```

## Dark Mode

All components support dark mode via CSS variables. No additional code needed:

```tsx
// Works automatically in both light and dark mode
<Card>
  <CardContent>
    <Input placeholder="Supports dark mode" />
    <Button>Click me</Button>
  </CardContent>
</Card>
```

## Accessibility Tips

```tsx
// Always provide labels
<div>
  <label htmlFor="email">Email</label>
  <Input id="email" type="email" />
</div>

// Use aria-label for icon buttons
<Button variant="ghost" size="icon" aria-label="Close">
  <X />
</Button>

// Provide helpful error messages
<Input 
  type="email" 
  aria-invalid={hasError}
  aria-describedby="email-error"
/>
{hasError && <span id="email-error">Invalid email</span>}
```

---

All components are production-ready and follow best practices for accessibility, TypeScript, and React patterns.
