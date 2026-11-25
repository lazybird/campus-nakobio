import { Editor, Node, mergeAttributes } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import { Table } from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableHeader from '@tiptap/extension-table-header';
import TableCell from '@tiptap/extension-table-cell';

export type CalloutVariant = 'alert' | 'tip';

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    callout: {
      toggleCallout: (variant: CalloutVariant) => ReturnType;
    };
  }
}

const Callout = Node.create({
  name: 'callout',
  group: 'block',
  content: 'inline*',
  defining: true,

  addAttributes() {
    return {
      variant: {
        default: 'alert' as CalloutVariant,
        parseHTML: (element) =>
          element.classList.contains('callout-tip') ? 'tip' : 'alert',
        renderHTML: (attributes) => ({
          class: attributes.variant === 'tip' ? 'callout-tip' : 'slide-alert',
        }),
      },
    };
  },

  parseHTML() {
    return [{ tag: 'div.slide-alert' }, { tag: 'div.callout-tip' }];
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(HTMLAttributes), 0];
  },

  addCommands() {
    return {
      toggleCallout:
        (variant: CalloutVariant) =>
        ({ editor, commands }) => {
          if (editor.isActive('callout', { variant })) {
            return commands.setNode('paragraph');
          }
          if (editor.isActive('callout')) {
            return commands.updateAttributes('callout', { variant });
          }
          return commands.setNode('callout', { variant });
        },
    };
  },
});

export interface CmsRichTextController {
  setContent: (html: string) => void;
  getHTML: () => string;
  focus: () => void;
  destroy: () => void;
  runAction: (action: string) => void;
  isActive: (action: string) => boolean;
}

export function createCmsRichTextEditor(
  element: HTMLElement,
  initialHtml: string,
  onUpdateState?: () => void
): CmsRichTextController {
  const editor = new Editor({
    element,
    extensions: [
      StarterKit.configure({
        heading: { levels: [2, 3] },
      }),
      Callout,
      Table.configure({ resizable: false }),
      TableRow,
      TableHeader,
      TableCell,
    ],
    content: initialHtml,
    onSelectionUpdate: () => onUpdateState?.(),
    onTransaction: () => onUpdateState?.(),
  });

  return {
    setContent(html: string) {
      editor.commands.setContent(html || '<p></p>', { emitUpdate: false });
      onUpdateState?.();
    },
    getHTML() {
      return editor.getHTML().trim();
    },
    focus() {
      editor.commands.focus('end');
    },
    destroy() {
      editor.destroy();
    },
    runAction(action: string) {
      const chain = editor.chain().focus();
      switch (action) {
        case 'bold':
          chain.toggleBold().run();
          break;
        case 'italic':
          chain.toggleItalic().run();
          break;
        case 'strike':
          chain.toggleStrike().run();
          break;
        case 'h2':
          chain.toggleHeading({ level: 2 }).run();
          break;
        case 'h3':
          chain.toggleHeading({ level: 3 }).run();
          break;
        case 'p':
          chain.setParagraph().run();
          break;
        case 'bulletList':
          chain.toggleBulletList().run();
          break;
        case 'orderedList':
          chain.toggleOrderedList().run();
          break;
        case 'blockquote':
          chain.toggleBlockquote().run();
          break;
        case 'alert':
          chain.toggleCallout('alert').run();
          break;
        case 'tip':
          chain.toggleCallout('tip').run();
          break;
        case 'table':
          if (editor.isActive('table')) {
            chain.addRowAfter().run();
          } else {
            chain.insertTable({ rows: 3, cols: 2, withHeaderRow: true }).run();
          }
          break;
        case 'tableDelete':
          if (editor.isActive('table')) {
            chain.deleteTable().run();
          }
          break;
        case 'undo':
          chain.undo().run();
          break;
        case 'redo':
          chain.redo().run();
          break;
      }
      onUpdateState?.();
    },
    isActive(action: string): boolean {
      switch (action) {
        case 'bold':
          return editor.isActive('bold');
        case 'italic':
          return editor.isActive('italic');
        case 'strike':
          return editor.isActive('strike');
        case 'h2':
          return editor.isActive('heading', { level: 2 });
        case 'h3':
          return editor.isActive('heading', { level: 3 });
        case 'p':
          return editor.isActive('paragraph') && !editor.isActive('callout');
        case 'bulletList':
          return editor.isActive('bulletList');
        case 'orderedList':
          return editor.isActive('orderedList');
        case 'blockquote':
          return editor.isActive('blockquote');
        case 'alert':
          return editor.isActive('callout', { variant: 'alert' });
        case 'tip':
          return editor.isActive('callout', { variant: 'tip' });
        case 'table':
          return editor.isActive('table');
        default:
          return false;
      }
    },
  };
}
