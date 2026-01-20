'use client';

import React, { createContext, useContext, useState, useCallback, useRef, ReactNode } from 'react';
import {
    getStores,
    getProducts,
    getDecisions,
    getInventoryStatusSummary,
    getDemandInsights,
    getTrendInsights,
    getInventoryInsights,
    getReplenishmentInsights,
    getTrends,
    getCampaignSuggestions,
    getPricingInsights
} from '@/lib/api';
import type { Store, Product, Decision } from '@/lib/types';

const CACHE_TTL = 10 * 60 * 1000; // 10 minutes

interface CacheEntry<T> {
    data: T;
    timestamp: number;
}

interface DataContextType {
    // Cached data (direct access)
    stores: Store[];
    products: Product[];
    decisions: Decision[];
    inventorySummary: any;
    trends: any[];
    campaignSuggestions: any[];

    // Loading states
    isLoading: boolean;

    // Fetch functions (use cache if valid)
    fetchStores: () => Promise<Store[]>;
    fetchProducts: () => Promise<Product[]>;
    fetchDecisions: () => Promise<Decision[]>;
    fetchInventorySummary: () => Promise<any>;

    // Agent insights (keyed by storeId)
    fetchDemandInsights: (storeId?: string) => Promise<any>;
    fetchTrendInsights: (storeId?: string) => Promise<any>;
    fetchInventoryInsights: (storeId?: string) => Promise<any>;
    fetchReplenishmentInsights: (storeId?: string) => Promise<any>;
    fetchPricingInsights: (storeId?: string) => Promise<any>;

    // Trends & Campaigns
    fetchTrends: () => Promise<any[]>;
    fetchCampaignSuggestions: () => Promise<any[]>;

    // Force refresh (bypass cache)
    refreshStores: () => Promise<Store[]>;
    refreshProducts: () => Promise<Product[]>;
    refreshDecisions: () => Promise<Decision[]>;
    refreshAll: () => Promise<void>;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const DataProvider = ({ children }: { children: ReactNode }) => {
    // Use refs for all caches to avoid closure issues
    const storesCache = useRef<CacheEntry<Store[]> | null>(null);
    const productsCache = useRef<CacheEntry<Product[]> | null>(null);
    const decisionsCache = useRef<CacheEntry<Decision[]> | null>(null);
    const inventoryCache = useRef<CacheEntry<any> | null>(null);

    // Agent insights caches (keyed by storeId)
    const demandInsightsCache = useRef<Record<string, CacheEntry<any>>>({});
    const trendInsightsCache = useRef<Record<string, CacheEntry<any>>>({});
    const inventoryInsightsCache = useRef<Record<string, CacheEntry<any>>>({});
    const replenishmentInsightsCache = useRef<Record<string, CacheEntry<any>>>({});
    const pricingInsightsCache = useRef<Record<string, CacheEntry<any>>>({});

    // Trends & Campaigns caches
    const trendsCache = useRef<CacheEntry<any[]> | null>(null);
    const campaignSuggestionsCache = useRef<CacheEntry<any[]> | null>(null);

    // State for triggering re-renders when cache updates
    const [, forceUpdate] = useState(0);
    const [isLoading, setIsLoading] = useState(false);

    const triggerUpdate = () => forceUpdate(n => n + 1);

    const isCacheValid = <T,>(cache: CacheEntry<T> | null): boolean => {
        if (!cache) return false;
        return Date.now() - cache.timestamp < CACHE_TTL;
    };

    const isKeyedCacheValid = (cache: Record<string, CacheEntry<any>>, key: string): boolean => {
        const entry = cache[key];
        if (!entry) return false;
        return Date.now() - entry.timestamp < CACHE_TTL;
    };

    // Fetch Stores
    const fetchStores = useCallback(async (): Promise<Store[]> => {
        if (isCacheValid(storesCache.current)) {
            console.log('[Cache] Using cached stores');
            return storesCache.current!.data;
        }
        console.log('[Cache] Fetching stores from API');
        setIsLoading(true);
        try {
            const data = await getStores();
            storesCache.current = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const refreshStores = useCallback(async (): Promise<Store[]> => {
        setIsLoading(true);
        try {
            const data = await getStores();
            storesCache.current = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Fetch Products
    const fetchProducts = useCallback(async (): Promise<Product[]> => {
        if (isCacheValid(productsCache.current)) {
            console.log('[Cache] Using cached products');
            return productsCache.current!.data;
        }
        console.log('[Cache] Fetching products from API');
        setIsLoading(true);
        try {
            const data = await getProducts();
            productsCache.current = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const refreshProducts = useCallback(async (): Promise<Product[]> => {
        setIsLoading(true);
        try {
            const data = await getProducts();
            productsCache.current = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Fetch Decisions
    const fetchDecisions = useCallback(async (): Promise<Decision[]> => {
        if (isCacheValid(decisionsCache.current)) {
            console.log('[Cache] Using cached decisions');
            return decisionsCache.current!.data;
        }
        console.log('[Cache] Fetching decisions from API');
        setIsLoading(true);
        try {
            const data = await getDecisions();
            decisionsCache.current = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const refreshDecisions = useCallback(async (): Promise<Decision[]> => {
        setIsLoading(true);
        try {
            const data = await getDecisions();
            decisionsCache.current = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Fetch Inventory Summary
    const fetchInventorySummary = useCallback(async (): Promise<any> => {
        if (isCacheValid(inventoryCache.current)) {
            console.log('[Cache] Using cached inventory summary');
            return inventoryCache.current!.data;
        }
        console.log('[Cache] Fetching inventory summary from API');
        setIsLoading(true);
        try {
            const data = await getInventoryStatusSummary();
            inventoryCache.current = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Agent Insights - Demand
    const fetchDemandInsights = useCallback(async (storeId?: string): Promise<any> => {
        const key = storeId || '__all__';
        if (isKeyedCacheValid(demandInsightsCache.current, key)) {
            console.log(`[Cache] Using cached demand insights for ${key}`);
            return demandInsightsCache.current[key].data;
        }
        console.log(`[Cache] Fetching demand insights for ${key} from API`);
        setIsLoading(true);
        try {
            const data = await getDemandInsights(storeId);
            demandInsightsCache.current[key] = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Agent Insights - Trend
    const fetchTrendInsights = useCallback(async (storeId?: string): Promise<any> => {
        const key = storeId || '__all__';
        if (isKeyedCacheValid(trendInsightsCache.current, key)) {
            console.log(`[Cache] Using cached trend insights for ${key}`);
            return trendInsightsCache.current[key].data;
        }
        console.log(`[Cache] Fetching trend insights for ${key} from API`);
        setIsLoading(true);
        try {
            const data = await getTrendInsights(storeId);
            trendInsightsCache.current[key] = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Agent Insights - Inventory
    const fetchInventoryInsights = useCallback(async (storeId?: string): Promise<any> => {
        const key = storeId || '__all__';
        if (isKeyedCacheValid(inventoryInsightsCache.current, key)) {
            console.log(`[Cache] Using cached inventory insights for ${key}`);
            return inventoryInsightsCache.current[key].data;
        }
        console.log(`[Cache] Fetching inventory insights for ${key} from API`);
        setIsLoading(true);
        try {
            const data = await getInventoryInsights(storeId);
            inventoryInsightsCache.current[key] = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Agent Insights - Replenishment
    const fetchReplenishmentInsights = useCallback(async (storeId?: string): Promise<any> => {
        const key = storeId || '__all__';
        if (isKeyedCacheValid(replenishmentInsightsCache.current, key)) {
            console.log(`[Cache] Using cached replenishment insights for ${key}`);
            return replenishmentInsightsCache.current[key].data;
        }
        console.log(`[Cache] Fetching replenishment insights for ${key} from API`);
        setIsLoading(true);
        try {
            const data = await getReplenishmentInsights(storeId);
            replenishmentInsightsCache.current[key] = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Agent Insights - Pricing
    const fetchPricingInsights = useCallback(async (storeId?: string): Promise<any> => {
        const key = storeId || '__all__';
        if (isKeyedCacheValid(pricingInsightsCache.current, key)) {
            console.log(`[Cache] Using cached pricing insights for ${key}`);
            return pricingInsightsCache.current[key].data;
        }
        console.log(`[Cache] Fetching pricing insights for ${key} from API`);
        setIsLoading(true);
        try {
            const data = await getPricingInsights(storeId);
            pricingInsightsCache.current[key] = { data, timestamp: Date.now() };
            triggerUpdate();
            return data;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Trends
    const fetchTrends = useCallback(async (): Promise<any[]> => {
        if (isCacheValid(trendsCache.current)) {
            console.log('[Cache] Using cached trends');
            return trendsCache.current!.data;
        }
        console.log('[Cache] Fetching trends from API');
        setIsLoading(true);
        try {
            const data = await getTrends();
            trendsCache.current = { data: data || [], timestamp: Date.now() };
            triggerUpdate();
            return data || [];
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Campaign Suggestions
    const fetchCampaignSuggestions = useCallback(async (): Promise<any[]> => {
        if (isCacheValid(campaignSuggestionsCache.current)) {
            console.log('[Cache] Using cached campaign suggestions');
            return campaignSuggestionsCache.current!.data;
        }
        console.log('[Cache] Fetching campaign suggestions from API');
        setIsLoading(true);
        try {
            const data = await getCampaignSuggestions();
            campaignSuggestionsCache.current = { data: data || [], timestamp: Date.now() };
            triggerUpdate();
            return data || [];
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Refresh All Data
    const refreshAll = useCallback(async () => {
        setIsLoading(true);
        try {
            const [stores, products, decisions, inventory] = await Promise.all([
                getStores(),
                getProducts(),
                getDecisions(),
                getInventoryStatusSummary(),
            ]);
            const now = Date.now();
            storesCache.current = { data: stores, timestamp: now };
            productsCache.current = { data: products, timestamp: now };
            decisionsCache.current = { data: decisions, timestamp: now };
            inventoryCache.current = { data: inventory, timestamp: now };
            // Clear agent insights caches on full refresh
            demandInsightsCache.current = {};
            trendInsightsCache.current = {};
            inventoryInsightsCache.current = {};
            replenishmentInsightsCache.current = {};
            pricingInsightsCache.current = {};
            triggerUpdate();
        } finally {
            setIsLoading(false);
        }
    }, []);

    return (
        <DataContext.Provider value={{
            stores: storesCache.current?.data || [],
            products: productsCache.current?.data || [],
            decisions: decisionsCache.current?.data || [],
            inventorySummary: inventoryCache.current?.data || null,
            trends: trendsCache.current?.data || [],
            campaignSuggestions: campaignSuggestionsCache.current?.data || [],
            isLoading,
            fetchStores,
            fetchProducts,
            fetchDecisions,
            fetchInventorySummary,
            fetchDemandInsights,
            fetchTrendInsights,
            fetchInventoryInsights,
            fetchReplenishmentInsights,
            fetchPricingInsights,
            fetchTrends,
            fetchCampaignSuggestions,
            refreshStores,
            refreshProducts,
            refreshDecisions,
            refreshAll,
        }}>
            {children}
        </DataContext.Provider>
    );
};

export const useDataContext = () => {
    const context = useContext(DataContext);
    if (context === undefined) {
        throw new Error('useDataContext must be used within a DataProvider');
    }
    return context;
};
