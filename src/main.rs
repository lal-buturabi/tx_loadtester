
use ethers::prelude::*;
use ethers::utils::parse_units;
use std::sync::Arc;
use tokio::time::{Sleep, timeout, Duration};
use web3::transports::Http;
use web3::types::{TransactionParameters, U256, BlockNumber};
use web3::Web3;
use serde::{Serialize, Deserialize};
use reqwest::Proxy as RProxy;
use reqwest::{Client as RClient};
use hyper::{Client as HClient, Request, Uri};
use hyper_tls::HttpsConnector;
use hyper::client::HttpConnector;
use hyper_proxy::{Proxy as HProxy, ProxyConnector, Intercept};
// #[tokio::main]
// fn main() -> anyhow::Result<()> {
//
//     let rpc_url = "";
//     let pvt_key = "";
//     let recipient = "";
//     let amt_eth = "0.000000000000000001";
//
//     let proxies = vec![
//         ""
//     ];
// }
#[derive(serde::Deserialize)]
struct Proxy {
    proxy: String,
    protocol: String,
    ip: String,
    port: u16,
    https: bool,
    anonymity: String,
    score: i32,
    geolocation: GeoLocation,
}

#[derive(Deserialize)]
struct GeoLocation {
    country: String,
    city: String,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let rpc_url = "https://sepolia.infura.io/v3/4e0625c5f11f4c7b97100b9c95984e13";
    let proxies_json_url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json";

    // Fetch the proxy list JSON
    let proxy_list: Vec<Proxy> = reqwest::get(proxies_json_url).await?.json().await?;
    println!("Total addresses: {}", proxy_list.len());
    // Check each proxy
    let mut tasks = Vec::new();
    for proxy in proxy_list {
        let rpc_url = rpc_url.to_string();
        let proxy_url = proxy.proxy.clone();

        tasks.push(tokio::spawn(async move {
            check_proxy(rpc_url, proxy_url).await
        }));
    }

    let mut working_proxies = Vec::new();
    for task in tasks {
        if let Ok(Some(proxy)) = task.await {
            working_proxies.push(proxy);
        }
    }

    println!("Working proxies: {:?}", working_proxies);

    Ok(())
}

async fn check_proxy(rpc_url: String, proxy_url: String) -> Option<String> {
    let proxy = {
        let proxy_uri = proxy_url.parse().unwrap();
        let mut proxy = HProxy::new(Intercept::All, proxy_uri);
        //proxy.set_authorization(Authorization::basic("John Doe", "Agent1234"));
        let http_con = HttpConnector::new();
       // let https_con = HttpsConnector::new();
        let proxy_connector = ProxyConnector::from_proxy(http_con, proxy).unwrap();
        proxy_connector
    };
    let https = HttpsConnector::new();
    // let client = RClient::builder().proxy(
    //     HProxy::new(Intercept::All, proxy_url.parse().unwrap())
    // ).build();
    let client = HClient::builder().build(proxy);

    let transport = Http::new(client, rpc_url.parse().ok()?).ok()?;
    let web3 = Web3::new(transport);

    let result = timeout(Duration::from_secs(10), web3.eth().block_number()).await;

    match result {
        Ok(Ok(_)) => Some(proxy_url),
        _ => None,
    }
}
