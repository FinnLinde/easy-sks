"use client";

import { useEffect, useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { listTopics, type Topic } from "@/services/topic/topic-service";
import type { TopicValue } from "@/services/study/study-service";

interface TopicFilterProps {
  value: TopicValue | undefined;
  onChange: (topic: TopicValue | undefined) => void;
}

export function TopicFilter({ value, onChange }: TopicFilterProps) {
  const [topics, setTopics] = useState<Topic[]>([]);

  useEffect(() => {
    listTopics().then(setTopics).catch(console.error);
  }, []);

  return (
    <Select
      value={value ?? "all"}
      onValueChange={(v) => onChange(v === "all" ? undefined : (v as TopicValue))}
    >
      <SelectTrigger className="w-full min-w-0 border-white/10 bg-card/70 sm:w-[260px]">
        <SelectValue placeholder="Alle Themen" />
      </SelectTrigger>
      <SelectContent className="border-white/10 bg-popover/95 backdrop-blur">
        <SelectItem value="all">Alle Themen</SelectItem>
        {topics.map((t) => (
          <SelectItem key={t.value} value={t.value}>
            {t.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
