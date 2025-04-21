"""
Tennis Match Data Exploratory Data Analysis by Year

This script performs exploratory data analysis on tennis match data by year,
analyzing individual years and creating a combined analysis for the last 5 years.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from pathlib import Path
import glob

plt.style.use("ggplot")
sns.set_palette("viridis")


class TennisYearlyEDA:
    def __init__(self, data_dir):
        """
        Initialize the EDA class with the path to the tennis data directory.

        Args:
            data_dir (str): Path to the directory containing yearly tennis match data CSV files
        """
        self.data_dir = Path(data_dir)
        self.yearly_data = {}
        self.combined_data = None

        self.base_output_dir = Path("eda_results")
        if not self.base_output_dir.exists():
            self.base_output_dir.mkdir(parents=True)

    def find_data_files(self):
        """Find all yearly tennis data files in the data directory."""
        pattern = os.path.join(self.data_dir, "atp_matches_*.csv")
        files = glob.glob(pattern)

        years = []
        for file in files:
            match = re.search(r"atp_matches_(\d{4})\.csv", os.path.basename(file))
            if match:
                years.append(int(match.group(1)))

        years.sort(reverse=True)

        return years

    def load_yearly_data(self, years=None):
        """
        Load tennis match data for specified years.

        Args:
            years (list): List of years to load. If None, load all available years.
        """
        if years is None:
            years = self.find_data_files()

        print(f"Loading data for years: {years}")

        for year in years:
            file_path = self.data_dir / f"atp_matches_{year}.csv"
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    self.yearly_data[year] = df
                    print(f"Loaded {year} data: {df.shape[0]} matches")
                except Exception as e:
                    print(f"Error loading {year} data: {e}")
            else:
                print(f"Data file for {year} not found at {file_path}")

    def load_last_n_years(self, n=5):
        """
        Load and combine data for the last n years.

        Args:
            n (int): Number of most recent years to load
        """
        all_years = self.find_data_files()
        recent_years = all_years[:n]

        print(f"Loading data for the last {n} years: {recent_years}")

        self.load_yearly_data(recent_years)

        dfs = []
        for year in recent_years:
            if year in self.yearly_data:
                df = self.yearly_data[year].copy()
                df["year"] = year
                dfs.append(df)

        if dfs:
            self.combined_data = pd.concat(dfs, ignore_index=True)
            print(
                f"Combined data for {len(dfs)} years: {self.combined_data.shape[0]} matches"
            )
        else:
            print("No data available for the specified years")

    def analyze_year(self, year):
        """
        Perform EDA for a specific year.

        Args:
            year (int): The year to analyze
        """
        if year not in self.yearly_data:
            print(f"No data loaded for {year}")
            return

        data = self.yearly_data[year]
        output_dir = self.base_output_dir / f"year_{year}"

        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        print(f"\n=== ANALYZING YEAR {year} ===")

        print(f"Dataset shape: {data.shape}")

        if "surface" in data.columns:
            surface_counts = data["surface"].value_counts()
            print("\nMatch counts by surface:")
            print(surface_counts)

            plt.figure(figsize=(10, 6))
            surface_counts.plot(kind="bar")
            plt.title(f"Number of Matches by Surface Type ({year})", fontsize=15)
            plt.xlabel("Surface", fontsize=12)
            plt.ylabel("Number of Matches", fontsize=12)
            plt.tight_layout()
            plt.savefig(output_dir / "matches_by_surface.png")
            plt.close()

        if "tourney_level" in data.columns:
            level_counts = data["tourney_level"].value_counts()
            print("\nTournament level distribution:")
            print(level_counts)

            plt.figure(figsize=(10, 6))
            level_counts.plot(kind="bar")
            plt.title(f"Number of Matches by Tournament Level ({year})", fontsize=15)
            plt.xlabel("Tournament Level", fontsize=12)
            plt.ylabel("Number of Matches", fontsize=12)
            plt.tight_layout()
            plt.savefig(output_dir / "matches_by_tournament_level.png")
            plt.close()

        if "minutes" in data.columns:
            duration_stats = data["minutes"].describe()
            print("\nMatch duration statistics (minutes):")
            print(duration_stats)

            plt.figure(figsize=(10, 6))
            sns.histplot(data["minutes"].dropna(), kde=True, bins=30)
            plt.axvline(
                duration_stats["mean"],
                color="red",
                linestyle="--",
                label=f"Mean: {duration_stats['mean']:.1f} min",
            )
            plt.axvline(
                duration_stats["50%"],
                color="green",
                linestyle="--",
                label=f"Median: {duration_stats['50%']:.1f} min",
            )
            plt.title(f"Distribution of Match Duration ({year})", fontsize=15)
            plt.xlabel("Duration (minutes)", fontsize=12)
            plt.ylabel("Frequency", fontsize=12)
            plt.legend()
            plt.tight_layout()
            plt.savefig(output_dir / "match_duration_distribution.png")
            plt.close()

        winner_counts = data["winner_name"].value_counts().head(10)
        print("\nTop 10 players by wins:")
        print(winner_counts)

        plt.figure(figsize=(12, 6))
        winner_counts.plot(kind="bar")
        plt.title(f"Top 10 Players by Number of Wins ({year})", fontsize=15)
        plt.xlabel("Player", fontsize=12)
        plt.ylabel("Number of Wins", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(output_dir / "top_players_by_wins.png")
        plt.close()

        with open(output_dir / "summary.txt", "w") as f:
            f.write(f"=== TENNIS DATA SUMMARY FOR {year} ===\n\n")
            f.write(f"Total matches: {data.shape[0]}\n\n")

            if "surface" in data.columns:
                f.write("Matches by surface:\n")
                for surface, count in surface_counts.items():
                    f.write(f"- {surface}: {count}\n")
                f.write("\n")

            if "tourney_level" in data.columns:
                f.write("Matches by tournament level:\n")
                for level, count in level_counts.items():
                    f.write(f"- {level}: {count}\n")
                f.write("\n")

            if "minutes" in data.columns:
                f.write("Match duration statistics (minutes):\n")
                for stat, value in duration_stats.items():
                    f.write(f"- {stat}: {value:.2f}\n")
                f.write("\n")

            f.write("Top 10 players by wins:\n")
            for player, wins in winner_counts.items():
                f.write(f"- {player}: {wins}\n")

        print(f"Analysis for {year} complete. Results saved to {output_dir}/")

    def analyze_combined_data(self):
        """Analyze the combined data from the last several years."""
        if self.combined_data is None:
            print("No combined data available. Please run load_last_n_years() first.")
            return

        output_dir = self.base_output_dir / "combined_analysis"
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        data = self.combined_data
        years = sorted(data["year"].unique())

        print(f"\n=== ANALYZING COMBINED DATA FOR YEARS {min(years)}-{max(years)} ===")
        print(f"Dataset shape: {data.shape}")

        matches_per_year = data.groupby("year").size()
        print("\nMatches per year:")
        print(matches_per_year)

        plt.figure(figsize=(10, 6))
        matches_per_year.plot(kind="bar")
        plt.title("Number of Matches per Year", fontsize=15)
        plt.xlabel("Year", fontsize=12)
        plt.ylabel("Number of Matches", fontsize=12)
        plt.tight_layout()
        plt.savefig(output_dir / "matches_per_year.png")
        plt.close()

        if "surface" in data.columns:
            surface_by_year = (
                data.groupby(["year", "surface"]).size().unstack(fill_value=0)
            )
            print("\nSurface distribution by year:")
            print(surface_by_year)

            plt.figure(figsize=(12, 8))
            surface_by_year.plot(kind="bar", stacked=True)
            plt.title("Surface Distribution by Year", fontsize=15)
            plt.xlabel("Year", fontsize=12)
            plt.ylabel("Number of Matches", fontsize=12)
            plt.legend(title="Surface")
            plt.tight_layout()
            plt.savefig(output_dir / "surface_by_year.png")
            plt.close()

        if "minutes" in data.columns:
            duration_by_year = data.groupby("year")["minutes"].agg(
                ["mean", "median", "std"]
            )
            print("\nMatch duration trends:")
            print(duration_by_year)

            plt.figure(figsize=(12, 6))
            duration_by_year["mean"].plot(marker="o", label="Mean")
            duration_by_year["median"].plot(marker="s", label="Median")
            plt.title("Match Duration Trends", fontsize=15)
            plt.xlabel("Year", fontsize=12)
            plt.ylabel("Duration (minutes)", fontsize=12)
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(output_dir / "duration_trends.png")
            plt.close()

        top_winners = data["winner_name"].value_counts().head(15)
        print("\nTop 15 players by wins across all years:")
        print(top_winners)

        plt.figure(figsize=(12, 8))
        top_winners.plot(kind="bar")
        plt.title(f"Top Players by Wins ({min(years)}-{max(years)})", fontsize=15)
        plt.xlabel("Player", fontsize=12)
        plt.ylabel("Number of Wins", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(output_dir / "top_players_combined.png")
        plt.close()

        top5_players = top_winners.index[:5]
        player_wins_by_year = pd.DataFrame()

        for player in top5_players:
            wins = data[data["winner_name"] == player].groupby("year").size()
            player_wins_by_year[player] = wins

        player_wins_by_year = player_wins_by_year.fillna(0)
        print("\nTop 5 players' wins by year:")
        print(player_wins_by_year)

        plt.figure(figsize=(12, 8))
        for player in player_wins_by_year.columns:
            plt.plot(
                player_wins_by_year.index,
                player_wins_by_year[player],
                marker="o",
                linewidth=2,
                label=player,
            )

        plt.title("Top Players Performance by Year", fontsize=15)
        plt.xlabel("Year", fontsize=12)
        plt.ylabel("Number of Wins", fontsize=12)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output_dir / "player_performance_by_year.png")
        plt.close()

        with open(output_dir / "summary.txt", "w") as f:
            f.write(
                f"=== TENNIS DATA SUMMARY FOR YEARS {min(years)}-{max(years)} ===\n\n"
            )
            f.write(f"Total matches: {data.shape[0]}\n\n")

            f.write("Matches per year:\n")
            for year, count in matches_per_year.items():
                f.write(f"- {year}: {count}\n")
            f.write("\n")

            if "surface" in data.columns:
                f.write("Surface distribution by year:\n")
                f.write(surface_by_year.to_string())
                f.write("\n\n")

            if "minutes" in data.columns:
                f.write("Match duration trends:\n")
                f.write(duration_by_year.to_string())
                f.write("\n\n")

            f.write("Top 15 players by wins across all years:\n")
            for player, wins in top_winners.items():
                f.write(f"- {player}: {wins}\n")
            f.write("\n")

            f.write("Top 5 players' wins by year:\n")
            f.write(player_wins_by_year.to_string())

        print(f"Combined analysis complete. Results saved to {output_dir}/")

    def run_yearly_analyses(self, years=None):
        """
        Run analyses for individual years.

        Args:
            years (list): List of years to analyze. If None, analyze all loaded years.
        """
        if years is None:
            years = list(self.yearly_data.keys())

        for year in years:
            if year in self.yearly_data:
                self.analyze_year(year)
            else:
                print(f"No data loaded for {year}")

    def run_all_analyses(self, last_n_years=5):
        """
        Run all analyses - individual years and combined.

        Args:
            last_n_years (int): Number of most recent years to include in combined analysis
        """
        all_years = self.find_data_files()
        print(f"Found data files for years: {all_years}")

        self.load_yearly_data(all_years)

        self.run_yearly_analyses()

        self.load_last_n_years(last_n_years)
        self.analyze_combined_data()

        print(f"\nAll analyses complete. Results saved to {self.base_output_dir}/")


if __name__ == "__main__":
    data_dir = "dataset"

    eda = TennisYearlyEDA(data_dir)
    eda.run_all_analyses(last_n_years=5)
