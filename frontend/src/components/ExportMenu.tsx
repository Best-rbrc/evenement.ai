import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Download, Copy, Calendar, FileText, Link as LinkIcon, Check } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface ExportMenuProps {
  calendarFile?: string;
  pdfFile?: string;
  formUrl?: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export function ExportMenu({ calendarFile, pdfFile, formUrl }: ExportMenuProps) {
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const handleDownloadCalendar = async () => {
    if (!calendarFile || calendarFile === 'Error') {
      toast({
        title: 'Calendar file not available',
        description: 'No calendar file was generated for this event.',
        variant: 'destructive',
      });
      return;
    }

    try {
      // Extract filename from path
      const filename = calendarFile.split('/').pop() || calendarFile.split('\\').pop() || 'event.ics';
      
      // Remove 'event_outputs/' prefix if present
      const filePath = calendarFile.replace(/^event_outputs[\/\\]/, '');
      
      // Fetch the file from the backend
      const response = await fetch(`${API_BASE_URL}/api/files/${encodeURIComponent(filePath)}`);
      
      if (!response.ok) {
        throw new Error(`Failed to download calendar file: ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: 'Calendar downloaded',
        description: `Downloaded ${filename}`,
      });
    } catch (error) {
      console.error('Calendar download error:', error);
      toast({
        title: 'Download failed',
        description: 'Could not download calendar file. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleDownloadPDF = async () => {
    if (!pdfFile) {
      toast({
        title: 'PDF not available',
        description: 'No PDF report was generated for this event.',
        variant: 'destructive',
      });
      return;
    }

    try {
      // Extract filename from path
      const filename = pdfFile.split('/').pop() || pdfFile.split('\\').pop() || 'event-proposal.pdf';
      
      // Remove 'event_outputs/' prefix if present
      const filePath = pdfFile.replace(/^event_outputs[\/\\]/, '');
      
      // Fetch the file from the backend
      const response = await fetch(`${API_BASE_URL}/api/files/${encodeURIComponent(filePath)}`);
      
      if (!response.ok) {
        throw new Error(`Failed to download PDF file: ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: 'PDF downloaded',
        description: `Downloaded ${filename}`,
      });
    } catch (error) {
      console.error('PDF download error:', error);
      toast({
        title: 'Download failed',
        description: 'Could not download PDF file. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleCopyFormUrl = async () => {
    if (!formUrl) {
      toast({
        title: 'Form URL not available',
        description: 'No registration form was created for this event.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await navigator.clipboard.writeText(formUrl);
      setCopied(true);
      toast({
        title: 'Link copied',
        description: 'Registration form URL copied to clipboard',
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Copy error:', error);
      toast({
        title: 'Copy failed',
        description: 'Could not copy link to clipboard. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const hasExports = (calendarFile && calendarFile !== 'Error') || pdfFile || formUrl;

  if (!hasExports) {
    return (
      <Button variant="default" size="sm" disabled>
        <Download className="w-4 h-4" />
        Export
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="default" size="sm">
          <Download className="w-4 h-4" />
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56" style={{ zIndex: 9999 }}>
        <DropdownMenuLabel>Export Options</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {calendarFile && calendarFile !== 'Error' && (
          <DropdownMenuItem onClick={handleDownloadCalendar}>
            <Calendar className="mr-2 h-4 w-4" />
            <span>Download Calendar (.ics)</span>
          </DropdownMenuItem>
        )}
        {pdfFile && (
          <DropdownMenuItem onClick={handleDownloadPDF}>
            <FileText className="mr-2 h-4 w-4" />
            <span>Download PDF Report</span>
          </DropdownMenuItem>
        )}
        {formUrl && (
          <DropdownMenuItem onClick={handleCopyFormUrl}>
            {copied ? (
              <>
                <Check className="mr-2 h-4 w-4" />
                <span>Link Copied!</span>
              </>
            ) : (
              <>
                <LinkIcon className="mr-2 h-4 w-4" />
                <span>Copy Registration Link</span>
              </>
            )}
          </DropdownMenuItem>
        )}
        {!hasExports && (
          <DropdownMenuItem disabled>
            <span className="text-muted-foreground">No exports available</span>
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

