import { existsSync, statSync } from 'node:fs';
import { join } from 'node:path';
import raw from '../data/downloads.json';

/**
 * 资源库数据：一份清单 `src/data/downloads.json`，多个页面共用。
 * - 本地文件（/files/xxx.zip）：构建时读磁盘，自动得到大小与最后修改时间
 * - 外部链接（https:// 开头）：按外链处理，不读磁盘
 */
export interface DownloadItem {
  /** 展示名称 */
  name: string;
  /** 文件路径（本地以 / 开头）或外部链接 */
  file: string;
  desc: string;
  date: string;
  version: string;
  tags: string[];
  /** 是否外部链接 */
  external: boolean;
  /** 文件名（带扩展名） */
  base: string;
  /** 人类可读的大小，如 2.31 MB */
  size: string;
  /** 本地文件不存在 */
  missing: boolean;
  /** 小写扩展名 */
  ext: string;
  /** 图标名（Icon.astro 里的 key） */
  icon: string;
  /** 下载用的文件名 */
  filename: string;
}

interface RawItem {
  name: string;
  file: string;
  desc?: string;
  date?: string;
  version?: string;
  tags?: string[];
}

export const isExternal = (f: string) => /^https?:\/\//i.test(f);

export const extOf = (f: string) => (f.split('?')[0].split('.').pop() || '').toLowerCase();

/** 按扩展名挑一个图标（没有就用通用的 download） */
export function iconFor(ext: string): string {
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) return 'archive';
  if (['pdf', 'doc', 'docx', 'md', 'txt', 'epub'].includes(ext)) return 'file';
  if (['png', 'jpg', 'jpeg', 'webp', 'gif', 'svg', 'psd'].includes(ext)) return 'image';
  if (['mp3', 'wav', 'flac', 'ogg', 'm4a'].includes(ext)) return 'music';
  if (['mp4', 'mkv', 'avi', 'mov', 'webm'].includes(ext)) return 'play_circle';
  if (['exe', 'msi', 'apk', 'dmg', 'iso'].includes(ext)) return 'cube';
  if (['js', 'ts', 'json', 'py', 'sh', 'go', 'rs', 'java', 'c', 'cpp'].includes(ext)) return 'code';
  return 'download';
}

export function fmtSize(bytes: number): string {
  if (!bytes) return '';
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} KB`;
  const mb = kb / 1024;
  if (mb < 1024) return `${mb.toFixed(2)} MB`;
  return `${(mb / 1024).toFixed(2)} GB`;
}

/** 读取全部资源条目（构建时执行一次） */
export function loadDownloads(): DownloadItem[] {
  return (raw as RawItem[]).map((it) => {
    const external = isExternal(it.file);
    const base = it.file.split('/').pop() || it.file;
    let size = '';
    let missing = false;
    let autoDate = '';

    if (!external) {
      const localPath = join(process.cwd(), 'public', it.file.replace(/^\//, ''));
      if (existsSync(localPath)) {
        const st = statSync(localPath);
        size = fmtSize(st.size);
        autoDate = st.mtime.toISOString().slice(0, 10);
      } else {
        missing = true;
      }
    }

    return {
      ...it,
      desc: it.desc ?? '',
      date: it.date ?? autoDate,
      version: it.version ?? '',
      tags: it.tags ?? [],
      external,
      base,
      size,
      missing,
      ext: extOf(it.file),
      icon: iconFor(extOf(it.file)),
      filename: base,
    };
  });
}

export const downloads = loadDownloads();
