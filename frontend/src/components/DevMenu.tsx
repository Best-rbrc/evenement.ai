import { useState } from 'react';
import { Settings, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface DevMenuProps {
  onSettingsChange?: (settings: DevSettings) => void;
}

export interface DevSettings {
  enableSandbox: boolean;
  enableSMS: boolean;
}

export function DevMenu({ onSettingsChange }: DevMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [settings, setSettings] = useState<DevSettings>({
    enableSandbox: false,
    enableSMS: false,
  });

  const handleToggle = (key: keyof DevSettings) => {
    const newSettings = {
      ...settings,
      [key]: !settings[key],
    };
    setSettings(newSettings);
    onSettingsChange?.(newSettings);
  };

  return (
    <>
      {/* Floating Dev Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-lg"
        variant="outline"
        size="icon"
      >
        {isOpen ? <X className="w-5 h-5" /> : <Settings className="w-5 h-5" />}
      </Button>

      {/* Dev Menu Panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-80">
          <Card className="shadow-2xl border-2">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Developer Settings
                </CardTitle>
                <Badge variant="secondary" className="text-xs">
                  DEV
                </Badge>
              </div>
              <CardDescription className="text-xs">
                Configure backend workflow options
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Sandbox Mode Toggle */}
              <div className="flex items-center justify-between space-x-2 p-3 rounded-lg bg-muted/50">
                <div className="flex-1">
                  <Label htmlFor="sandbox-mode" className="text-sm font-medium cursor-pointer">
                     Sandbox Mode
                  </Label>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Use sandboxed Docker MCP for forms
                  </p>
                </div>
                <Switch
                  id="sandbox-mode"
                  checked={settings.enableSandbox}
                  onCheckedChange={() => handleToggle('enableSandbox')}
                />
              </div>

              {/* SMS Notifications Toggle */}
              <div className="flex items-center justify-between space-x-2 p-3 rounded-lg bg-muted/50">
                <div className="flex-1">
                  <Label htmlFor="sms-mode" className="text-sm font-medium cursor-pointer">
                     SMS Notifications
                  </Label>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Send event details via SMS ($1/msg)
                  </p>
                </div>
                <Switch
                  id="sms-mode"
                  checked={settings.enableSMS}
                  onCheckedChange={() => handleToggle('enableSMS')}
                />
              </div>

              {/* Current Configuration */}
              <div className="pt-3 border-t text-xs space-y-1">
                <p className="text-muted-foreground">Current Config:</p>
                <div className="flex flex-col gap-1 pl-2">
                  <span className="font-mono">
                    Forms: {settings.enableSandbox ? ' Sandboxed (Docker)' : ' Unsandboxed (mcp-remote)'}
                  </span>
                  <span className="font-mono">
                    SMS: {settings.enableSMS ? ' Enabled' : ' Disabled'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
}
